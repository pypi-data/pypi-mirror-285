"""Simple SQLite-based synchronisation of HTTP API collections."""

import contextlib
import enum
import importlib.util
import json
import sqlite3
import sys
from dataclasses import field, dataclass
from datetime import datetime, timedelta, timezone
from functools import reduce
from types import SimpleNamespace
from typing import Generator, Iterable, Mapping, Sequence

import requests
import tqdm

from .utility import chunk_iter, parse_timestamp


# A breaking change in CPython 3.11 "resolved" in the docs:
# https://github.com/python/cpython/issues/100458
# https://docs.python.org/3/whatsnew/3.11.html#enum
if sys.version_info >= (3, 11):
    strenum = (enum.StrEnum,)  # noqa
else:
    strenum = (str, enum.Enum)  # nocov


class ColumnType(*strenum):
    integer = 'INTEGER'
    numeric = 'NUMERIC'
    text = 'TEXT'
    datetime = 'DATETIME'


@dataclass
class ExtractColumn:
    path: str
    type: ColumnType
    name: str | None = None
    pk: bool = False

    @property
    def column_def(self) -> str:
        name = self.name or self.path.replace('.', '_')
        args = 'PRIMARY KEY NOT NULL' if self.pk else ''
        return f'{name} {self.type} {args}'

    def extract_from(self, res: dict):
        result = reduce(dict.__getitem__, self.path.split('.'), res)
        if result and self.type is ColumnType.datetime:
            result = parse_timestamp(result).timestamp()  # type: ignore[wrong-arg-types]
        return result


@dataclass(frozen=True)
class SourceResourceCollection:
    url_path: str
    resource_id_key: str = 'id'
    resource_timestamp_key: str = 'created_at'
    request_params: Mapping = field(default_factory=dict, compare=False)
    page_size: int = 100


@dataclass(frozen=True)
class SourceSubresource:
    url_path_template: str
    collection_resource_id_key: str
    request_params: Mapping = field(default_factory=dict, compare=False)


@dataclass
class TargetTable:
    name: str
    extract_columns: Sequence[ExtractColumn] = (
        ExtractColumn('id', ColumnType.integer, name='table_id', pk=True),
        ExtractColumn('created_at', ColumnType.datetime),
    )


@dataclass
class SubResmap:
    resource: SourceSubresource
    table: TargetTable


@dataclass
class Resmap:
    collection: SourceResourceCollection
    table: TargetTable
    subresources: Sequence[SubResmap] = field(default_factory=list)

    sync_lookbehind: timedelta = timedelta(days=1)
    load_interval: timedelta = timedelta(days=365)


@dataclass
class Api:
    base_url: str
    default_headers: Mapping = field(default_factory=dict)


@dataclass
class ResmapFile:
    api: Api
    resources: Sequence[Resmap]

    @classmethod
    def load(cls, filepath: str) -> 'ResmapFile':
        spec = importlib.util.spec_from_file_location('resmapfile', filepath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # type: ignore[attribute-error]
        return cls(module.api, module.resources)


resmap_api = SimpleNamespace(
    Api=Api,
    Resmap=Resmap,
    SubResmap=SubResmap,
    SourceResourceCollection=SourceResourceCollection,
    SourceSubresource=SourceSubresource,
    ColumnType=ColumnType,
    ExtractColumn=ExtractColumn,
    TargetTable=TargetTable,
    timedelta=timedelta,
)


class SqliteStorage:
    """
    Simple SQLite-based document-style resource storage.

    Each table is expected to have a PK, ``{table_name}_id``, and
    a ``created_at`` extract columns.
    """

    chunk_size = 8192

    _conn: sqlite3.Connection

    def __init__(self, database: str):
        self._conn = sqlite3.connect(database)

    def create_res_table(self, target: TargetTable):
        sql = '''
            CREATE TABLE IF NOT EXISTS "{table}" (
                {extract_columns},
                data TEXT NOT NULL
            )
        '''.format(
            table=target.name,
            extract_columns=',\n'.join(ec.column_def for ec in target.extract_columns),
        )
        with self._conn:
            self._conn.execute(sql)

    def recreate_res_table(self, target: TargetTable):
        tmp_table_name = f'{target.name}_tmp'
        sql = f'ALTER TABLE "{target.name}" RENAME TO {tmp_table_name}'
        with self._conn:
            self._conn.execute(sql)

        self.create_res_table(target)
        self.upsert_res(self.fetch_res_column(tmp_table_name), target)

        sql = f'DROP TABLE {tmp_table_name}'
        with self._conn:
            self._conn.execute(sql)

    def upsert_res(self, resources: Iterable[dict], target: TargetTable):
        sql = 'INSERT OR REPLACE INTO "{table}" VALUES({placeholders})'.format(
            table=target.name,
            placeholders=','.join(['?'] * (1 + len(target.extract_columns)))
        )
        for chunk in chunk_iter(resources, self.chunk_size):
            values = [
                [
                    *(ec.extract_from(res) for ec in target.extract_columns),
                    json.dumps(res, sort_keys=True),
                ]
                for res in chunk
            ]
            with self._conn:
                self._conn.executemany(sql, values)

    def get_latest_res_timestamp(self, table: str) -> datetime | None:
        sql = f"""
            SELECT created_at
            FROM "{table}"
            ORDER BY 1 DESC
            LIMIT 1
        """
        row = self._conn.execute(sql).fetchone()
        return datetime.fromtimestamp(row[0], timezone.utc) if row else None

    def fetch_res_column(self, table: str) -> Iterable[dict]:
        sql = f'SELECT data FROM {table}'
        cursor = self._conn.execute(sql)
        while True:
            rows = cursor.fetchmany(self.chunk_size)
            if not rows:
                break
            yield from (json.loads(r[0]) for r in rows)

    def close(self):
        self._conn.close()


class CollectionLoader:
    _api: Api
    _verbose: bool

    _session: requests.Session

    def __init__(self, api: Api, verbose: bool):
        self._api = api
        self._verbose = verbose

        self._session = self._create_session()

    def _create_session(self) -> requests.Session:
        session = requests.Session()
        session.headers.update(self._api.default_headers)
        retry = requests.adapters.Retry(
            total=8,
            status_forcelist=(500, 502, 504),
            backoff_factor=0.5,  # min(120, bf * 2 ** n_previous_retries)
        )
        adapter = requests.adapters.HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

    def _iterate_pages(self, collection_url: str, params: Mapping) -> Iterable[dict]:
        page = 1
        while True:
            resp = self._session.get(collection_url, params={**params, 'page': page})
            resp.raise_for_status()
            page += 1

            result = resp.json()
            if not result:
                break

            yield result

    def _load_resources(self, src: SourceSubresource, ids: Iterable[str]) -> Iterable[dict]:
        for res_id in ids:
            res_url = self._api.base_url + src.url_path_template.format(id=res_id)
            resp = self._session.get(res_url, params=src.request_params)
            resp.raise_for_status()
            yield resp.json()

    @contextlib.contextmanager
    def _progress_indicator(self):
        if not self._verbose:
            yield type('Stub', (), {'update': lambda *args: 0})()
            return

        with tqdm.tqdm() as pi:
            yield pi

    def load_collection(
        self,
        source_collection: SourceResourceCollection,
        source_subresources: Sequence[SourceSubresource],
    ) -> Generator[tuple[SourceResourceCollection | SourceSubresource, dict], None, None]:
        collection_url = self._api.base_url + source_collection.url_path
        with self._progress_indicator() as pi:
            coll_params = source_collection.request_params
            for resources in self._iterate_pages(collection_url, params=coll_params):
                yield from ((source_collection, r) for r in resources)

                if source_subresources:
                    resource_ids = [r[source_collection.resource_id_key] for r in resources]
                    for src_subr in source_subresources:
                        subresources = self._load_resources(src_subr, resource_ids)
                        yield from (
                            (src_subr, {**sr, src_subr.collection_resource_id_key: rid})
                            for rid, sr in zip(resource_ids, subresources)
                        )

                pi.update(len(resources))
