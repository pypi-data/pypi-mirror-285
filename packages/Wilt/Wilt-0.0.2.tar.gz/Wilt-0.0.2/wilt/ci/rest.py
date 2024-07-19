import logging
from contextlib import closing
from datetime import datetime, timezone

from .. import resdb, utility


logger = logging.getLogger(__name__)


def sync_db_cmd(resmap_file: str, database_file: str, verbose: bool, **kwargs):
    resmap_file = resdb.ResmapFile.load(resmap_file)
    loader = resdb.CollectionLoader(resmap_file.api, verbose)
    with closing(resdb.SqliteStorage(database_file)) as store:
        for rm in resmap_file.resources:
            _sync_resmap(rm, loader, store)


def rebuild_db_cmd(table: list[str], resmap_file: str, database_file: str, **kwargs):
    req_table_names = dict.fromkeys(table)  # a set with preserved order
    if not req_table_names:
        return

    resmap_file = resdb.ResmapFile.load(resmap_file)
    known_tables = {}
    for rm in resmap_file.resources:
        known_tables[rm.table.name] = rm.table
        known_tables.update((sub_rm.table.name, sub_rm.table) for sub_rm in rm.subresources)

    unknown_req_table_names = req_table_names.keys() - known_tables.keys()
    if unknown_req_table_names:
        raise utility.CommandError(f'Unknown tables to rebuild: {unknown_req_table_names}')

    with closing(resdb.SqliteStorage(database_file)) as store:
        for t in [t for n, t in known_tables.items() if n in req_table_names]:
            logging.info('Rebuilding %s table', t.name)
            store.recreate_res_table(t)


def _sync_resmap(rm: resdb.Resmap, loader: resdb.CollectionLoader, store: resdb.SqliteStorage):
    store.create_res_table(rm.table)
    for srm in rm.subresources:
        store.create_res_table(srm.table)

    latest_res_ts = (
        store.get_latest_res_timestamp(rm.table.name)
        or datetime.fromtimestamp(0, timezone.utc)
    )
    full_load_start = datetime.now(timezone.utc) - rm.load_interval
    until_ts = max(latest_res_ts, full_load_start)
    logger.info('Synchronising %s until %s', rm.table.name, until_ts.replace(microsecond=0))

    ts_key = rm.collection.resource_timestamp_key
    src_resources = [sr.resource for sr in rm.subresources]
    with closing(loader.load_collection(rm.collection, src_resources)) as resource_gen:
        k: resdb.SourceResourceCollection | resdb.SourceSubresource
        table_map = {
            rm.collection: rm.table,
            **{subrm.resource: subrm.table for subrm in rm.subresources},
        }
        page_size = rm.collection.page_size
        for k, resources in utility.partition_pair_iter(resource_gen, page_size):
            store.upsert_res(resources, table_map[k])
            if k == rm.collection:
                oldest_res = max(resources, key=lambda r: r[ts_key])
                if utility.parse_timestamp(oldest_res[ts_key]) < until_ts:
                    break
