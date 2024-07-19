import io
import os
import pathlib
import tempfile
import textwrap
import unittest
from contextlib import closing
from datetime import datetime, timedelta, timezone
from unittest import mock

import pandas

from . import resdb, utility
from .ci import gitlab, rest
from .cq import wilt


class TestCqWilt(unittest.TestCase):

    def test_wilt(self):
        with open(unittest.__file__) as fp:
            self.assertGreater(wilt.wilt(fp), 0)

    def test_run_cmd(self):
        output = io.StringIO()
        path = pathlib.Path(unittest.__file__).parent
        wilt.run_cmd(list(path.glob('*.py')), indent=4, output_file=output)
        self.assertGreater(float(output.getvalue()), 0)


class TestResdbResmapfileApi(unittest.TestCase):

    def test_api(self):
        api = resdb.Api(
            base_url='https://gitlab.com/api/v4/projects/4961127',
            default_headers={'PRIVATE-TOKEN': 'S3Cr3t'},
        )
        self.assertEqual('https://gitlab.com/api/v4/projects/4961127', api.base_url)
        self.assertEqual({'PRIVATE-TOKEN': 'S3Cr3t'}, api.default_headers)

    def test_resmap(self):
        src = resdb.SourceResourceCollection(
            '/jobs',
            request_params={'per_page': 100, 'sort': 'desc'},
        )
        tgt = resdb.TargetTable(
            'job',
            extract_columns=[
                resdb.ExtractColumn('id', resdb.ColumnType.integer, name='job_id', pk=True),
                resdb.ExtractColumn('name', resdb.ColumnType.text),
                resdb.ExtractColumn('created_at', resdb.ColumnType.datetime),
                resdb.ExtractColumn('duration', resdb.ColumnType.numeric),
                resdb.ExtractColumn('status', resdb.ColumnType.text),
                resdb.ExtractColumn('pipeline.id', resdb.ColumnType.integer),
            ],
        )
        rm = resdb.Resmap(src, tgt, load_interval=resdb.timedelta(days=2 * 365))
        self.assertEqual(timedelta(days=1), rm.sync_lookbehind)
        self.assertEqual(timedelta(days=730), rm.load_interval)
        self.assertEqual(src, rm.collection)
        self.assertEqual(tgt, rm.table)

    def test_resmap_file(self):
        with tempfile.NamedTemporaryFile('w', suffix='.py') as f:
            f.write(textwrap.dedent('''
            from wilt.resdb import resmap_api as rm

            api = rm.Api(
              base_url='https://gitlab.com/api/v4/projects/4961127',
              default_headers={'PRIVATE-TOKEN': 'S3Cr3t'},
            )
            resources = [
              rm.Resmap(
                rm.SourceResourceCollection(
                  '/jobs',
                  request_params={'per_page': 100, 'sort': 'desc'},
                ),
                rm.TargetTable(
                  'job',
                  extract_columns=[
                    rm.ExtractColumn('id', rm.ColumnType.integer, name='job_id', pk=True),
                    rm.ExtractColumn('created_at', rm.ColumnType.datetime),
                    rm.ExtractColumn('name', rm.ColumnType.text),
                    rm.ExtractColumn('duration', rm.ColumnType.numeric),
                    rm.ExtractColumn('pipeline.id', rm.ColumnType.integer),
                  ],
                ),
              ),
              rm.Resmap(
                rm.SourceResourceCollection(
                  '/repository/commits',
                  request_params={'per_page': 100, 'sort': 'desc', 'all': True},
                ),
                rm.TargetTable(
                  'commit',
                  extract_columns=[
                    rm.ExtractColumn('id', rm.ColumnType.text, name='commit_id', pk=True),
                    rm.ExtractColumn('created_at', rm.ColumnType.datetime),
                  ],
                ),
              ),
            ]
            '''))
            f.flush()

            exec_locals = {}
            with open(f.name) as f1:
                exec(f1.read(), None, exec_locals)
            actual = resdb.ResmapFile.load(f.name)
            self.assertEqual(exec_locals['api'], actual.api)
            self.assertEqual(exec_locals['resources'], actual.resources)


class TestResdbExtractColumn(unittest.TestCase):

    def test_column_def(self):
        testee = resdb.ExtractColumn('foo', resdb.ColumnType.integer)
        self.assertEqual('foo INTEGER ', testee.column_def)

        testee = resdb.ExtractColumn('foo.bar', resdb.ColumnType.numeric)
        self.assertEqual('foo_bar NUMERIC ', testee.column_def)

        testee = resdb.ExtractColumn('foo.bar', resdb.ColumnType.text, name='override')
        self.assertEqual('override TEXT ', testee.column_def)

        testee = resdb.ExtractColumn('id', resdb.ColumnType.integer, name='override', pk=True)
        self.assertEqual('override INTEGER PRIMARY KEY NOT NULL', testee.column_def)

    def test_extract_from(self):
        testee = resdb.ExtractColumn('foo', resdb.ColumnType.integer)
        self.assertEqual(2, testee.extract_from({'foo': 2}))

        testee = resdb.ExtractColumn('foo.bar', resdb.ColumnType.integer)
        self.assertEqual(2, testee.extract_from({'foo': {'bar': 2}}))

    def test_extract_from_datetime(self):
        testee = resdb.ExtractColumn('ts', resdb.ColumnType.datetime)
        self.assertEqual(1706181745.0, testee.extract_from({'ts': '2024-01-25T11:22:25+00:00'}))
        self.assertEqual(1706178145.0, testee.extract_from({'ts': '2024-01-25T11:22:25+01:00'}))


class TestResdbSqliteStorage(unittest.TestCase):

    def test_create_res_table(self):
        table = resdb.TargetTable(
            'job',
            extract_columns=[
                resdb.ExtractColumn('id', resdb.ColumnType.integer, name='job_id', pk=True),
                resdb.ExtractColumn('name', resdb.ColumnType.text),
                resdb.ExtractColumn('created_at', resdb.ColumnType.datetime),
                resdb.ExtractColumn('duration', resdb.ColumnType.numeric),
                resdb.ExtractColumn('status', resdb.ColumnType.text),
                resdb.ExtractColumn('pipeline.id', resdb.ColumnType.integer),
            ],
        )
        expected = [
            (0, 'job_id', 'INTEGER', 1, None, 1),
            (1, 'name', 'TEXT', 0, None, 0),
            (2, 'created_at', 'DATETIME', 0, None, 0),
            (3, 'duration', 'NUMERIC', 0, None, 0),
            (4, 'status', 'TEXT', 0, None, 0),
            (5, 'pipeline_id', 'INTEGER', 0, None, 0),
            (6, 'data', 'TEXT', 1, None, 0)
        ]
        with closing(resdb.SqliteStorage(':memory:')) as testee:
            testee.create_res_table(table)

            actual = testee._conn.execute('PRAGMA table_info(job)').fetchall()
            self.assertEqual(expected, actual)

    def test_recreate_res_table(self):
        table = resdb.TargetTable(
            'job',
            extract_columns=[
                resdb.ExtractColumn('id', resdb.ColumnType.integer, name='job_id', pk=True),
                resdb.ExtractColumn('created_at', resdb.ColumnType.datetime),
            ],
        )
        with closing(resdb.SqliteStorage(':memory:')) as testee:
            testee.create_res_table(table)
            testee.upsert_res([
                {'id': 1, 'created_at': '2020-06-17T11:42:47.091Z', 'name': 'Die Eier Von Satan'},
                {'id': 2, 'created_at': '2010-07-16T11:24:48.011Z', 'name': 'Useful Idiot'},
            ], table)

            table = resdb.TargetTable(
                'job',
                extract_columns=[
                    resdb.ExtractColumn('id', resdb.ColumnType.integer, name='job_id', pk=True),
                    resdb.ExtractColumn('created_at', resdb.ColumnType.datetime),
                    resdb.ExtractColumn('name', resdb.ColumnType.text),
                ],
            )
            testee.recreate_res_table(table)

            actual = testee._conn.execute('SELECT name FROM job').fetchall()
            self.assertEqual([('Die Eier Von Satan',), ('Useful Idiot',)], actual)

    def test_upsert_res_new(self):
        table = resdb.TargetTable(
            'job',
            extract_columns=[
                resdb.ExtractColumn('id', resdb.ColumnType.integer, name='job_id', pk=True),
                resdb.ExtractColumn('created_at', resdb.ColumnType.datetime),
            ],
        )
        with closing(resdb.SqliteStorage(':memory:')) as testee:
            testee.create_res_table(table)
            testee.upsert_res([
                {'id': 1, 'created_at': '2020-06-17T11:42:47Z', 'name': 'Die Eier Von Satan'},
                {'id': 2, 'created_at': '2010-07-16T11:24:48Z', 'name': 'Useful Idiot'},
            ], table)

            actual = testee._conn.execute('SELECT * FROM job').fetchall()

        expected =  [
            (
                1,
                1592394167,
                '{"created_at": "2020-06-17T11:42:47Z", "id": 1, "name": "Die Eier Von Satan"}',
            ),
            (
                2,
                1279279488,
                '{"created_at": "2010-07-16T11:24:48Z", "id": 2, "name": "Useful Idiot"}',
            ),
        ]
        self.assertEqual(expected, actual)

    def test_upsert_res_mix(self):
        table = resdb.TargetTable(
            'job',
            extract_columns=[
                resdb.ExtractColumn('id', resdb.ColumnType.integer, name='job_id', pk=True),
                resdb.ExtractColumn('created_at', resdb.ColumnType.datetime),
            ],
        )
        with closing(resdb.SqliteStorage(':memory:')) as testee:
            testee.create_res_table(table)
            testee.upsert_res([
                {'id': 1, 'created_at': '2020-06-17T11:42:47Z', 'name': 'Die Eier Von Satan'},
                {'id': 2, 'created_at': '2010-07-16T11:24:48Z', 'name': 'Useful Idiot'},
            ], table)
            self.assertEqual(2, testee._conn.execute('SELECT COUNT(*) FROM job').fetchone()[0])
            testee.upsert_res([
                {'id': 1, 'created_at': '2020-06-17T11:42:47Z', 'name': 'Eulogy'},
                {'id': 2, 'created_at': '2010-07-16T11:24:48Z', 'name': 'Useful Idiot'},
                {'id': 3, 'created_at': '2010-07-18T11:45:16Z', 'name': 'Cesaro Summability'},
            ], table)
            self.assertEqual(3, testee._conn.execute('SELECT COUNT(*) FROM job').fetchone()[0])

            actual = testee._conn.execute('SELECT * FROM job').fetchall()

        expected =  [
            (
                1,
                1592394167,
                '{"created_at": "2020-06-17T11:42:47Z", "id": 1, "name": "Eulogy"}',
            ),
            (
                2,
                1279279488,
                '{"created_at": "2010-07-16T11:24:48Z", "id": 2, "name": "Useful Idiot"}',
            ),
            (
                3,
                1279453516,
                '{"created_at": "2010-07-18T11:45:16Z", "id": 3, "name": "Cesaro Summability"}',
            ),
        ]
        self.assertEqual(expected, actual)

    def test_get_latest_res_timestamp(self):
        table = resdb.TargetTable(
            'job',
            extract_columns=[
                resdb.ExtractColumn('id', resdb.ColumnType.integer, name='job_id', pk=True),
                resdb.ExtractColumn('created_at', resdb.ColumnType.datetime),
            ],
        )

        with closing(resdb.SqliteStorage(':memory:')) as testee:
            testee.create_res_table(table)
            self.assertEqual(None, testee.get_latest_res_timestamp('job'))

        with closing(resdb.SqliteStorage(':memory:')) as testee:
            testee.create_res_table(table)
            testee.upsert_res([
                {'id': 1, 'created_at': '2020-06-17T11:42:47Z', 'name': 'Die Eier Von Satan'},
                {'id': 2, 'created_at': '2010-07-16T11:24:48Z', 'name': 'Useful Idiot'},
            ], table)
            self.assertEqual(
                datetime(2020, 6, 17, 11, 42, 47, tzinfo=timezone.utc),
                testee.get_latest_res_timestamp('job'),
            )

    def test_fetch_res_column(self):
        table = resdb.TargetTable(
            'job',
            extract_columns=[
                resdb.ExtractColumn('id', resdb.ColumnType.integer, name='job_id', pk=True),
                resdb.ExtractColumn('created_at', resdb.ColumnType.datetime),
            ],
        )
        with closing(resdb.SqliteStorage(':memory:')) as testee:
            testee.create_res_table(table)
            testee.upsert_res([
                {'id': 1, 'created_at': '2020-06-17T11:42:47Z', 'name': 'Die Eier Von Satan'},
                {'id': 2, 'created_at': '2010-07-16T11:24:48Z', 'name': 'Useful Idiot'},
            ], table)
            actual = list(testee.fetch_res_column('job'))

        expected = [
            {'created_at': '2020-06-17T11:42:47Z', 'id': 1, 'name': 'Die Eier Von Satan'},
            {'created_at': '2010-07-16T11:24:48Z', 'id': 2, 'name': 'Useful Idiot'},
        ]
        self.assertEqual(expected, actual)


class TestResdbCollectionLoader(unittest.TestCase):

    def test_load_collection(self):
        api = resdb.Api(
            base_url='https://gitlab.com/api/v4/projects/4961127',
            default_headers={'PRIVATE-TOKEN': 'S3Cr3t'},
        )
        testee = resdb.CollectionLoader(api, verbose=False)
        src = resdb.SourceResourceCollection(
            '/jobs', request_params={'per_page': 100, 'sort': 'desc'},
        )

        responses = [
            None,
            [{'res': 3}, {'res': 4}],
            [{'res': 1}, {'res': 2}],
        ]
        with mock.patch.object(testee._session, 'get') as get_mock:
            get_mock.return_value.json.side_effect = responses.pop
            actual = list(testee.load_collection(src, []))

        self.assertEqual([
            (src, {'res': 1}),
            (src, {'res': 2}),
            (src, {'res': 3}),
            (src, {'res': 4}),
        ], actual)
        get_mock.assert_has_calls([
            mock.call(api.base_url + src.url_path, params={**src.request_params, 'page': 1}),
            mock.call(api.base_url + src.url_path, params={**src.request_params, 'page': 2}),
            mock.call(api.base_url + src.url_path, params={**src.request_params, 'page': 3}),
        ], any_order=True)

    def test_load_collection_with_subresources(self):
        api = resdb.Api(
            base_url='https://gitlab.com/api/v4/projects/4961127',
            default_headers={'PRIVATE-TOKEN': 'S3Cr3t'},
        )
        testee = resdb.CollectionLoader(api, verbose=False)

        src = resdb.SourceResourceCollection(
            '/pipelines',
            resource_id_key='res_id',
            request_params={'per_page': 25, 'sort': 'desc'},
            page_size=25,
        )
        src_sub_list = [
            resdb.SourceSubresource('/pipelines/{id}', 'pipeline_id'),
            resdb.SourceSubresource('/pipelines/{id}/test_report', 'pipeline_id'),
        ]

        responses = [
            None,
            {'type': 'subres2', 'b': 40},
            {'type': 'subres2', 'b': 30},
            {'type': 'subres1', 'a': 40},
            {'type': 'subres1', 'a': 30},
            [{'res_id': 3}, {'res_id': 4}],
            {'type': 'subres2', 'b': 20},
            {'type': 'subres2', 'b': 10},
            {'type': 'subres1', 'a': 20},
            {'type': 'subres1', 'a': 10},
            [{'res_id': 1}, {'res_id': 2}],
        ]
        with mock.patch.object(testee._session, 'get') as get_mock:
            get_mock.return_value.json.side_effect = responses.pop
            actual = list(testee.load_collection(src, src_sub_list))

        self.assertEqual([
            (src, {'res_id': 1}),
            (src, {'res_id': 2}),
            (src_sub_list[0], {'a': 10, 'pipeline_id': 1, 'type': 'subres1'}),
            (src_sub_list[0], {'a': 20, 'pipeline_id': 2, 'type': 'subres1'}),
            (src_sub_list[1], {'b': 10, 'pipeline_id': 1, 'type': 'subres2'}),
            (src_sub_list[1], {'b': 20, 'pipeline_id': 2, 'type': 'subres2'}),
            (src, {'res_id': 3}),
            (src, {'res_id': 4}),
            (src_sub_list[0], {'a': 30, 'pipeline_id': 3, 'type': 'subres1'}),
            (src_sub_list[0], {'a': 40, 'pipeline_id': 4, 'type': 'subres1'}),
            (src_sub_list[1], {'b': 30, 'pipeline_id': 3, 'type': 'subres2'}),
            (src_sub_list[1], {'b': 40, 'pipeline_id': 4, 'type': 'subres2'}),
        ], actual)

        res_url = api.base_url + src.url_path
        subres1_url_tpl = api.base_url + src_sub_list[0].url_path_template
        subres2_url_tpl = api.base_url + src_sub_list[1].url_path_template
        get_mock.assert_has_calls([
            mock.call(res_url, params={**src.request_params, 'page': 1}),
            mock.call(subres1_url_tpl.format(id=1), params={}),
            mock.call(subres1_url_tpl.format(id=2), params={}),
            mock.call(subres2_url_tpl.format(id=1), params={}),
            mock.call(subres2_url_tpl.format(id=2), params={}),
            mock.call(res_url, params={**src.request_params, 'page': 2}),
            mock.call(subres1_url_tpl.format(id=3), params={}),
            mock.call(subres1_url_tpl.format(id=4), params={}),
            mock.call(subres2_url_tpl.format(id=3), params={}),
            mock.call(subres2_url_tpl.format(id=4), params={}),
            mock.call(res_url, params={**src.request_params, 'page': 3}),
        ], any_order=True)


class TestCiRest(unittest.TestCase):

    def get_resmapfile(self) -> str:
        return textwrap.dedent('''
            from wilt.resdb import resmap_api as rm

            api = rm.Api(
              base_url='https://gitlab.com/api/v4/projects/4961127',
              default_headers={'PRIVATE-TOKEN': 'S3Cr3t'},
            )
            resources = [
              rm.Resmap(
                rm.SourceResourceCollection(
                  '/pipelines',
                  request_params={'per_page': 25, 'sort': 'desc'},
                  page_size=25,
                ),
                rm.TargetTable(
                  'pipeline_short',
                  extract_columns=[
                    rm.ExtractColumn(
                      'id', rm.ColumnType.integer, name='pipeline_short_id', pk=True
                    ),
                    rm.ExtractColumn('created_at', rm.ColumnType.datetime),
                  ],
                ),
                subresources=[
                  rm.SubResmap(
                    rm.SourceSubresource('/pipelines/{id}', 'pipeline_id'),
                    rm.TargetTable(
                      'pipeline',
                      extract_columns=[
                        rm.ExtractColumn(
                          'id', rm.ColumnType.integer, name='pipeline_id', pk=True
                        ),
                        rm.ExtractColumn('created_at', rm.ColumnType.datetime),
                        rm.ExtractColumn('status', rm.ColumnType.text),
                      ],
                    ),
                  ),
                  rm.SubResmap(
                    rm.SourceSubresource(
                      '/pipelines/{id}/test_report', 'pipeline_id',
                    ),
                    rm.TargetTable(
                      'test_report',
                      extract_columns=[
                        rm.ExtractColumn(
                          'pipeline_id', rm.ColumnType.integer, name='pipeline_id', pk=True
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              rm.Resmap(
                rm.SourceResourceCollection(
                  '/repository/commits',
                  request_params={'per_page': 100, 'sort': 'desc', 'all': True},
                ),
                rm.TargetTable(
                  'commit',
                  extract_columns=[
                    rm.ExtractColumn('id', rm.ColumnType.text, name='commit_id', pk=True),
                    rm.ExtractColumn('created_at', rm.ColumnType.datetime),
                  ],
                ),
              ),
            ]
        ''')

    def test_sync_db_cmd(self):
        with tempfile.NamedTemporaryFile('w', suffix='.py') as f:
            f.write(self.get_resmapfile())
            f.flush()

            with mock.patch('wilt.ci.rest._sync_resmap') as m:
                rest.sync_db_cmd(f.name, f.name, verbose=False)

            self.assertEqual('/pipelines', m.call_args_list[0][0][0].collection.url_path)
            self.assertEqual('/repository/commits', m.call_args_list[1][0][0].collection.url_path)
            self.assertEqual(2, len(m.call_args_list))

    def test_sync_resmap_first(self):
        src = resdb.SourceResourceCollection(
            '/jobs', request_params={'per_page': 100, 'sort': 'desc'}
        )
        tgt = resdb.TargetTable(
            'job',
            extract_columns=[
                resdb.ExtractColumn('id', resdb.ColumnType.integer, name='job_id', pk=True),
                resdb.ExtractColumn('created_at', resdb.ColumnType.datetime),
            ],
        )
        rm = resdb.Resmap(src, tgt)

        def load_collection(source_collection, _source_subresources):
            yield source_collection, {'job_id': 2, 'created_at': '2024-01-25T11:22:25+00:00'}
            yield source_collection, {'job_id': 1, 'created_at': '2024-01-25T11:22:24+00:00'}

        storage_mock = mock.Mock(spec=resdb.SqliteStorage)
        storage_mock.get_latest_res_timestamp.return_value = None
        loader_mock = mock.Mock(spec=resdb.CollectionLoader)
        loader_mock.load_collection.side_effect = load_collection
        rest._sync_resmap(rm, loader_mock, storage_mock)
        self.assertEqual([
            mock.call.create_res_table(tgt),
            mock.call.get_latest_res_timestamp('job'),
            mock.call.upsert_res(
                (
                    {'job_id': 2, 'created_at': '2024-01-25T11:22:25+00:00'},
                    {'job_id': 1, 'created_at': '2024-01-25T11:22:24+00:00'},
                ), tgt
            ),
        ], storage_mock.method_calls)
        self.assertEqual([mock.call.load_collection(src, [])], loader_mock.method_calls)

    def test_sync_resmap_subsequent(self):
        src = resdb.SourceResourceCollection(
            '/jobs', request_params={'per_page': 2, 'sort': 'desc'}, page_size=2,
        )
        tgt = resdb.TargetTable(
            'job',
            extract_columns=[
                resdb.ExtractColumn('id', resdb.ColumnType.integer, name='job_id', pk=True),
                resdb.ExtractColumn('created_at', resdb.ColumnType.datetime),
            ],
        )
        rm = resdb.Resmap(src, tgt)

        def load_collection(source_collection, _source_subresources):
            yield source_collection, {'job_id': 5, 'created_at': '2024-01-25T11:22:28+00:00'}
            yield source_collection, {'job_id': 4, 'created_at': '2024-01-25T11:22:27+00:00'}
            yield source_collection, {'job_id': 3, 'created_at': '2024-01-25T11:22:26+00:00'}
            yield source_collection, {'job_id': 2, 'created_at': '2024-01-25T11:22:25+00:00'}
            self.fail('Last record is expected to be skipped')  # nocov

        storage_mock = mock.Mock(spec=resdb.SqliteStorage)
        storage_mock.get_latest_res_timestamp.return_value = (
            datetime(2024, 1, 25, 11, 22, 28, tzinfo=timezone.utc)
        )
        loader_mock = mock.Mock(spec=resdb.CollectionLoader)
        loader_mock.load_collection.side_effect = load_collection

        rest._sync_resmap(rm, loader_mock, storage_mock)

        self.assertEqual([
            mock.call.create_res_table(tgt),
            mock.call.get_latest_res_timestamp('job'),
            mock.call.upsert_res(
                (
                    {'job_id': 5, 'created_at': '2024-01-25T11:22:28+00:00'},
                    {'job_id': 4, 'created_at': '2024-01-25T11:22:27+00:00'},
                ), tgt
            ),
            mock.call.upsert_res(
                (
                    {'job_id': 3, 'created_at': '2024-01-25T11:22:26+00:00'},
                    {'job_id': 2, 'created_at': '2024-01-25T11:22:25+00:00'},
                ), tgt
            ),
        ], storage_mock.method_calls)
        self.assertEqual([mock.call.load_collection(src, [])], loader_mock.method_calls)

    def test_sync_resmap_empty_collection(self):
        src = resdb.SourceResourceCollection(
            '/jobs', request_params={'per_page': 100, 'sort': 'desc'}
        )
        tgt = resdb.TargetTable(
            'job',
            extract_columns=[
                resdb.ExtractColumn('id', resdb.ColumnType.integer, name='job_id', pk=True),
                resdb.ExtractColumn('created_at', resdb.ColumnType.datetime),
            ],
        )
        rm = resdb.Resmap(src, tgt)

        def load_collection(*args):
            return
            yield

        storage_mock = mock.Mock(spec=resdb.SqliteStorage)
        storage_mock.get_latest_res_timestamp.return_value = None
        loader_mock = mock.Mock(spec=resdb.CollectionLoader)
        loader_mock.load_collection.side_effect = load_collection

        rest._sync_resmap(rm, loader_mock, storage_mock)

        self.assertEqual([
            mock.call.create_res_table(tgt),
            mock.call.get_latest_res_timestamp('job'),
        ], storage_mock.method_calls)
        self.assertEqual([mock.call.load_collection(src, [])], loader_mock.method_calls)

    def test_sync_resmap_with_subresources(self):
        src = resdb.SourceResourceCollection(
            '/pipelines', request_params={'per_page': 100, 'sort': 'desc'}
        )
        tgt = resdb.TargetTable(
            'pipeline_short',
            extract_columns=[
                resdb.ExtractColumn(
                    'id', resdb.ColumnType.integer, name='pipeline_short_id', pk=True
                ),
                resdb.ExtractColumn('created_at', resdb.ColumnType.datetime),
            ],
        )
        full_pipeline_sub = resdb.SourceSubresource('/pipelines/{id}', 'pipeline_id')
        test_report_sub = resdb.SourceSubresource('/pipelines/{id}/test_report', 'pipeline_id')
        subresources = [
            resdb.SubResmap(
                full_pipeline_sub,
                resdb.TargetTable(
                    'pipeline',
                    extract_columns=[
                        resdb.ExtractColumn(
                            'id', resdb.ColumnType.integer, name='pipeline_id', pk=True
                        ),
                        resdb.ExtractColumn('duration', resdb.ColumnType.numeric),
                    ],
                ),
            ),
            resdb.SubResmap(
                test_report_sub,
                resdb.TargetTable(
                    'test_report',
                    extract_columns=[
                        resdb.ExtractColumn(
                            'pipeline_id', resdb.ColumnType.integer, name='pipeline_id', pk=True
                        ),
                    ],
                ),
            ),
        ]
        rm = resdb.Resmap(src, tgt, subresources=subresources)

        def load_collection(source_collection, _source_subresources):
            yield source_collection, {'id': 2, 'created_at': '2024-01-25T11:22:25+00:00'}
            yield source_collection, {'id': 1, 'created_at': '2024-01-25T11:22:24+00:00'}
            yield full_pipeline_sub, {'full': 'pipeline 2'}
            yield full_pipeline_sub, {'full': 'pipeline 1'}
            yield test_report_sub, {'test_report': 'pipeline 2'}
            yield test_report_sub, {'test_report': 'pipeline 1'}

        storage_mock = mock.Mock(spec=resdb.SqliteStorage)
        storage_mock.get_latest_res_timestamp.return_value = None
        loader_mock = mock.Mock(spec=resdb.CollectionLoader)
        loader_mock.load_collection.side_effect = load_collection

        rest._sync_resmap(rm, loader_mock, storage_mock)

        self.assertEqual([
            mock.call.create_res_table(tgt),
            mock.call.create_res_table(subresources[0].table),
            mock.call.create_res_table(subresources[1].table),
            mock.call.get_latest_res_timestamp('pipeline_short'),
            mock.call.upsert_res(
                (
                    {'id': 2, 'created_at': '2024-01-25T11:22:25+00:00'},
                    {'id': 1, 'created_at': '2024-01-25T11:22:24+00:00'},
                ), tgt
            ),
            mock.call.upsert_res(
                ({'full': 'pipeline 2'}, {'full': 'pipeline 1'}),
                subresources[0].table,
            ),
            mock.call.upsert_res(
                ({'test_report': 'pipeline 2'}, {'test_report': 'pipeline 1'}),
                subresources[1].table,
            ),
        ], storage_mock.method_calls)
        self.assertEqual(
            [mock.call.load_collection(src, [full_pipeline_sub, test_report_sub])],
            loader_mock.method_calls,
        )

    def test_rebuild_db_cmd(self):
        with tempfile.NamedTemporaryFile('w', suffix='.py') as f:
            f.write(self.get_resmapfile())
            f.flush()

            storage_mock = mock.Mock(spec=resdb.SqliteStorage)
            storage_mock_cls = mock.Mock(return_value=storage_mock)
            with mock.patch('wilt.ci.rest.resdb.SqliteStorage', storage_mock_cls):
                rest.rebuild_db_cmd(['test_report', 'pipeline_short'], f.name, ':memory:')

        storage_mock.method_calls = [
            mock.call.recreate_res_table(
                resdb.TargetTable(
                    name='pipeline_short',
                    extract_columns=[
                        resdb.ExtractColumn(
                            path='id',
                            type=resdb.ColumnType.integer,
                            name='pipeline_short_id',
                            pk=True,
                        ),
                        resdb.ExtractColumn(path='created_at', type=resdb.ColumnType.datetime)
                    ],
                )
            ),
            mock.call.recreate_res_table(
                resdb.TargetTable(
                    name='test_report',
                    extract_columns=[
                        resdb.ExtractColumn(
                            path='pipeline_id',
                            type=resdb.ColumnType.integer,
                            name='pipeline_id',
                            pk=True,
                        )
                    ],
                )
            ),
            mock.call.close()
        ]

    def test_rebuild_db_cmd_unknown(self):
        with tempfile.NamedTemporaryFile('w', suffix='.py') as f:
            f.write(self.get_resmapfile())
            f.flush()

            with self.assertRaises(utility.CommandError) as ctx:
                rest.rebuild_db_cmd(['test_report', 'foo'], f.name, ':memory:')
            self.assertEqual("Unknown tables to rebuild: {'foo'}", str(ctx.exception))

    def test_rebuild_db_cmd_empty(self):
        with self.assertNoLogs('wilt.ci.rest', 'INFO'):
            rest.rebuild_db_cmd([], '/dev/null', ':memory:')


class TestCiGitlab(unittest.TestCase):

    storage: resdb.SqliteStorage
    table: resdb.TargetTable

    def setUp(self):
        self.storage = resdb.SqliteStorage(':memory:')
        self.addCleanup(self.storage.close)

        self.table = resdb.TargetTable(
            'pipeline',
            extract_columns=[
                resdb.ExtractColumn('id', resdb.ColumnType.integer, name='pipeline_id', pk=True),
                resdb.ExtractColumn('created_at', resdb.ColumnType.datetime),
                resdb.ExtractColumn('duration', resdb.ColumnType.numeric),
                resdb.ExtractColumn('ref', resdb.ColumnType.text),
            ],
        )
        self.storage.create_res_table(self.table)

    def get_pipeline_resources(self):
        header = ['created_at', 'duration', 'queued_duration', 'ref', 'status', 'id']
        rows = [
            ['2024-07-06T12:13:20.815Z', 2062, 17, 'branch/default', 'success', 43033],
            ['2024-06-30T16:27:05.732Z', 2121, 5, 'branch/default', 'success', 41864],
            ['2024-06-30T15:38:52.029Z', 983, 645, '1.11.1', 'success', 41862],
            ['2024-06-30T15:38:51.390Z', None, None, 'branch/default', 'canceled', 41861],
            ['2024-06-30T15:14:40.692Z', 2058, 50, 'branch/default', 'success', 41860],
            ['2024-06-26T06:24:44.210Z', 1961, 33, 'branch/default', 'success', 41167],
            ['2024-06-25T21:51:45.982Z', 1915, 20, 'branch/default', 'failed', 41154],
            ['2024-06-23T13:35:02.284Z', 1995, 34, 'branch/default', 'success', 40707],
            ['2024-06-23T12:39:04.504Z', 1901, 27, 'branch/default', 'success', 40705],
            ['2024-06-23T11:31:21.471Z', 1897, 335, 'branch/default', 'success', 40704],
            ['2024-06-23T11:05:09.508Z', 1895, 14, 'branch/default', 'success', 40703],
            ['2024-06-23T10:13:52.079Z', 1906, 48, 'branch/default', 'success', 40702],
            ['2024-06-23T09:39:38.036Z', 1914, 12, 'branch/default', 'failed', 40701],
            ['2024-06-23T08:48:47.198Z', 1915, 9, 'branch/default', 'failed', 40700],
            ['2024-06-23T08:03:38.330Z', 2167, 13, 'branch/default', 'failed', 40699],
            ['2024-06-22T19:51:17.083Z', 2234, 1563, 'branch/default', 'success', 40696],
            ['2024-06-22T19:39:04.653Z', 2256, 25, 'branch/default', 'success', 40695],
            ['2024-06-21T17:45:54.062Z', 2244, 54, 'branch/default', 'success', 40654],
            ['2024-06-21T17:31:05.090Z', 257, 11, 'branch/default', 'failed', 40650],
            ['2024-05-09T09:34:32.292Z', 2327, 1, 'branch/default', 'success', 33006],
            ['2024-05-09T08:35:03.450Z', 2324, 2, 'branch/default', 'success', 32989],
            ['2024-05-09T07:19:30.337Z', 2331, 2, 'branch/default', 'success', 32965],
            ['2024-05-07T12:09:12.958Z', 2330, 2409, 'branch/default', 'success', 32630],
            ['2024-05-07T10:43:38.968Z', 2101, 3, 'branch/default', 'success', 32601],
            ['2024-05-06T21:57:28.247Z', 293, 12, 'branch/default', 'failed', 32533],
            ['2024-05-06T21:52:41.011Z', 295, 3, 'branch/default', 'failed', 32532],
            ['2024-05-06T21:32:23.845Z', 296, 2, 'branch/default', 'failed', 32530],
            ['2024-05-06T15:43:30.147Z', 286, 398, 'branch/default', 'failed', 32475],
            ['2024-05-06T14:49:58.895Z', 2001, 1, 'branch/default', 'failed', 32460],
            ['2024-05-05T10:09:24.391Z', 1681, 1, 'branch/default', 'success', 32335],
            ['2024-05-05T09:16:33.733Z', 1796, 1, 'branch/default', 'failed', 32334],
            ['2024-05-04T20:46:53.785Z', 1746, 3, 'branch/default', 'success', 32331],
            ['2024-05-04T19:59:28.504Z', 1803, 2, 'branch/default', 'success', 32330],
            ['2024-04-21T21:57:09.769Z', 1548, 3, 'branch/default', 'success', 30303],
            ['2024-02-26T22:31:43.086Z', 1910, 3, 'branch/default', 'success', 22680],
            ['2024-02-25T22:42:04.069Z', 1517, 3, 'branch/default', 'success', 22488],
            ['2024-02-15T20:24:37.366Z', 1675, 58, 'branch/default', 'success', 21338],
            ['2024-02-15T20:06:15.381Z', 44, 3, 'branch/default', 'canceled', 21336],
            ['2024-02-15T19:25:10.279Z', 1764, 1, 'branch/default', 'success', 21331],
            ['2024-02-14T17:56:32.864Z', 1474, 1, 'branch/default', 'success', 21097],
            ['2024-02-14T17:15:34.087Z', 1392, 2, 'branch/default', 'failed', 21087],
            ['2023-10-26T17:39:19.455Z', 1423, 674, 'branch/default', 'success', 5993],
            ['2023-10-26T17:26:48.195Z', 1418, 3, 'branch/default', 'failed', 5955],
            ['2023-10-26T16:43:59.626Z', 1547, 1, 'branch/default', 'success', 5953],
            ['2023-10-07T10:28:58.968Z', 1534, 2, 'branch/default', 'success', 5139],
            ['2023-10-04T21:07:48.601Z', 1508, 2, 'branch/default', 'success', 5065],
            ['2023-10-04T20:34:38.443Z', 1405, 182, 'branch/default', 'success', 5064],
            ['2023-10-04T20:27:11.388Z', None, None, 'branch/default', 'canceled', 5063],
            ['2023-10-04T20:22:18.193Z', 841, 2, 'branch/default', 'failed', 5062],
            ['2023-10-04T19:35:40.125Z', 1400, 1, 'branch/default', 'success', 5061],
            ['2023-10-04T17:56:24.722Z', 1288, 1, 'branch/default', 'failed', 5058],
            ['2023-09-30T14:10:36.289Z', 1394, 1, 'branch/default', 'success', 4982],
            ['2023-09-29T21:39:03.893Z', 1325, 1, 'branch/default', 'success', 4966],
            ['2023-09-22T18:21:39.342Z', 1315, 2, 'branch/default', 'success', 4896],
            ['2023-09-22T17:16:04.385Z', 1301, 560, 'branch/default', 'success', 4892],
            ['2023-09-22T17:03:24.602Z', 1314, 2, 'branch/default', 'success', 4891],
            ['2023-09-03T22:22:50.869Z', 1387, 920, 'branch/default', 'success', 4676],
            ['2023-09-03T22:14:43.616Z', 1379, 25, 'branch/default', 'success', 4675],
            ['2023-09-03T21:52:05.962Z', 1378, None, 'branch/default', 'success', 4674],
            ['2023-09-03T21:34:37.121Z', None, None, 'branch/default', 'canceled', 4672],
            ['2023-09-03T21:28:28.139Z', 407, 3, 'branch/default', 'failed', 4670],
            ['2023-07-31T17:12:23.738Z', 1329, 1, 'branch/default', 'success', 4363],
            ['2023-07-31T15:11:44.040Z', 1329, 2, 'branch/default', 'success', 4359],
            ['2023-07-22T21:14:18.346Z', 1366, 24, 'branch/default', 'success', 4282],
            ['2023-07-22T21:12:35.471Z', 117, 2, 'branch/default', 'canceled', 4281],
            ['2023-07-22T20:37:59.831Z', 1286, 374, 'branch/default', 'success', 4280],
            ['2023-07-22T20:19:58.444Z', 1450, 2, 'branch/default', 'failed', 4279],
            ['2023-07-18T21:53:20.971Z', 1411, None, 'branch/default', 'success', 4245],
            ['2023-07-18T21:35:46.745Z', 41, 258, 'branch/default', 'canceled', 4243],
            ['2023-07-18T21:33:53.451Z', None, None, 'branch/default', 'canceled', 4242],
            ['2023-07-18T21:15:40.836Z', 1334, 126, 'branch/default', 'success', 4241],
            ['2023-07-18T20:56:37.285Z', 1240, 27, 'branch/default', 'failed', 4239],
            ['2023-07-18T20:55:16.566Z', None, None, 'branch/default', 'canceled', 4238],
            ['2023-07-18T20:44:30.548Z', 659, 3, 'branch/default', 'failed', 4237],
            ['2023-04-16T20:27:45.440Z', 1525, None, 'branch/default', 'success', 3588],
            ['2022-11-13T12:02:08.472Z', 1542, 543, 'branch/default', 'success', 2534],
            ['2022-11-06T11:14:04.514Z', 1541, 3, 'branch/default', 'success', 2523],
            ['2022-11-05T22:03:53.029Z', 1525, 363, 'branch/default', 'success', 2522],
            ['2022-11-05T21:44:42.346Z', 1510, 1, 'branch/default', 'failed', 2521],
            ['2022-11-05T21:39:17.501Z', None, None, 'branch/default', 'failed', 2520],
            ['2022-09-18T15:20:48.759Z', 1475, 2, 'branch/default', 'success', 2413],
            ['2022-09-18T14:35:14.922Z', 288, 2, 'branch/default', 'canceled', 2411],
            ['2022-09-18T14:06:51.249Z', 1573, 2, 'branch/default', 'success', 2410],
            ['2022-09-04T11:04:53.316Z', 1573, 2, 'branch/default', 'success', 2332],
            ['2022-09-03T20:12:14.732Z', None, None, 'branch/default', 'canceled', 2330],
            ['2022-09-03T20:06:09.091Z', 1588, 3, 'branch/default', 'success', 2329],
            ['2022-08-31T20:31:35.059Z', 1555, 1, 'branch/default', 'success', 2314],
            ['2022-08-30T17:22:47.899Z', 1545, 457, 'branch/default', 'failed', 2313],
            ['2022-08-30T17:04:21.547Z', 1557, 3, 'branch/default', 'failed', 2312],
            ['2022-08-28T11:54:54.582Z', 1730, 1, 'branch/default', 'success', 2311],
            ['2022-08-01T13:11:16.330Z', 1490, 2, 'branch/default', 'success', 2278],
            ['2022-07-31T17:00:13.116Z', 1510, 2, 'branch/default', 'success', 2277],
            ['2022-05-29T16:48:11.494Z', 1316, 3, 'branch/default', 'success', 2124],
            ['2022-05-29T15:16:11.660Z', 1365, 1, 'branch/default', 'success', 2120],
            ['2021-12-26T15:38:44.876Z', 1315, 1670, 'branch/default', 'success', 1060],
            ['2021-12-26T15:36:50.204Z', 1316, 5, 'branch/default', 'success', 1058],
            ['2021-12-25T16:05:33.191Z', 1421, 5, 'branch/default', 'success', 1057],
            ['2021-12-04T20:53:04.850Z', 1291, 579, 'branch/default', 'success', 1034],
            ['2021-12-04T20:41:15.592Z', 1277, 8, 'branch/default', 'success', 1033],
            ['2021-12-04T16:10:47.528Z', 1294, 6, 'branch/default', 'success', 1031],
            ['2021-12-04T15:48:16.928Z', 1277, 5, 'branch/default', 'success', 1028],
            ['2021-11-13T17:32:12.066Z', 1243, 654, 'branch/default', 'success', 991],
            ['2021-11-13T17:22:14.667Z', 1244, 4, 'branch/default', 'success', 990],
            ['2021-10-31T14:25:56.804Z', 1210, 7, 'branch/default', 'success', 968],
            ['2021-10-30T19:33:11.980Z', 1186, 3, 'branch/default', 'success', 967],
            ['2021-10-29T21:26:19.806Z', 1228, 6, 'branch/default', 'success', 966],
            ['2021-10-29T21:01:06.571Z', 806, 486, 'branch/default', 'failed', 965],
            ['2021-10-29T20:50:20.931Z', 1126, 2, 'branch/default', 'failed', 964],
            ['2021-10-29T20:29:44.737Z', 1206, 5, 'branch/default', 'success', 963],
            ['2021-10-29T20:04:10.030Z', 1199, 2, 'branch/default', 'success', 962],
            ['2021-10-29T19:29:45.790Z', 1116, 6, 'branch/default', 'failed', 961],
            ['2021-10-27T14:40:13.582Z', 1141, 8, 'branch/default', 'success', 950],
            ['2021-10-26T19:32:51.662Z', 1412, 277, 'branch/default', 'success', 947],
            ['2021-10-26T19:18:42.730Z', None, None, 'branch/default', 'canceled', 946],
            ['2021-10-26T19:09:32.259Z', 1402, 272, 'branch/default', 'success', 945],
            ['2021-10-26T19:06:56.302Z', 103, 6, 'branch/default', 'canceled', 944],
            ['2021-10-26T12:29:32.708Z', 1488, 51, 'branch/default', 'success', 943],
            ['2021-10-26T12:11:35.045Z', 601, 439, 'branch/default', 'failed', 942],
            ['2021-10-26T11:56:11.397Z', 1358, 2, 'branch/default', 'failed', 941],
            ['2021-10-25T19:47:23.980Z', 1297, 4, 'branch/default', 'failed', 939],
            ['2021-10-25T11:01:50.570Z', 1387, 5, 'branch/default', 'success', 933],
            ['2021-10-25T09:42:00.466Z', 1410, 6, 'branch/default', 'success', 932],
            ['2021-10-24T21:55:13.804Z', 1401, 1113, 'branch/default', 'failed', 931],
            ['2021-10-24T21:49:40.328Z', 1440, 4, 'branch/default', 'failed', 930],
            ['2021-10-24T18:35:52.885Z', 1463, 6, 'branch/default', 'success', 929],
            ['2021-10-24T18:03:50.052Z', 1492, 5, 'branch/default', 'success', 928],
            ['2021-10-24T13:14:03.904Z', 1456, 4, 'branch/default', 'success', 920],
            ['2021-10-09T20:40:00.633Z', 1178, 8, 'branch/default', 'success', 899],
            ['2021-10-09T20:35:51.098Z', 170, 5, 'branch/default', 'failed', 898],
            ['2021-10-09T18:26:20.446Z', 1193, 6, 'branch/default', 'success', 897],
            ['2021-08-28T14:47:38.752Z', 1363, 480, 'branch/default', 'success', 858],
            ['2021-08-08T15:08:51.073Z', 1467, 1854, 'branch/default', 'success', 853],
            ['2021-08-08T15:08:00.175Z', 1457, 3, 'branch/default', 'success', 851],
            ['2021-08-08T14:42:38.657Z', 1423, 3, 'branch/default', 'success', 850],
            ['2021-08-08T13:11:21.311Z', 1414, 1, 'branch/default', 'failed', 849],
            ['2021-08-08T12:10:59.484Z', 1481, 2, 'branch/default', 'success', 848],
            ['2021-08-08T10:35:20.649Z', 1419, 2, 'branch/default', 'success', 847],
            ['2021-08-07T21:39:22.300Z', 1356, 3, 'branch/default', 'failed', 846],
            ['2021-08-07T11:32:43.229Z', 1321, 3, 'branch/default', 'failed', 841],
            ['2021-05-22T15:43:32.491Z', 1402, 1, 'branch/default', 'success', 766],
            ['2021-05-22T15:10:09.076Z', 1400, 1, 'branch/default', 'success', 765],
            ['2021-05-15T14:16:16.708Z', 1450, 2, 'branch/default', 'success', 761],
            ['2021-05-10T21:07:35.585Z', 1496, None, 'branch/default', 'success', 760],
            ['2021-05-10T06:50:31.628Z', 1510, 1, 'branch/default', 'success', 759],
            ['2021-05-10T05:21:43.289Z', 1438, 73, 'branch/default', 'failed', 758],
            ['2021-05-09T20:49:55.266Z', 1473, 2, 'branch/default', 'success', 756],
            ['2021-05-09T17:09:11.756Z', 1415, 2, 'branch/default', 'success', 755],
            ['2021-05-09T15:42:33.492Z', 1450, 3, 'branch/default', 'success', 754],
            ['2021-05-09T11:56:15.134Z', 1433, 133, 'branch/default', 'success', 753],
            ['2021-04-27T16:28:29.985Z', 1340, 1, 'branch/default', 'success', 739],
            ['2021-04-26T10:14:02.630Z', 1320, 2, 'branch/default', 'success', 736],
            ['2021-04-26T09:35:29.265Z', 1342, 2, 'branch/default', 'success', 735],
            ['2021-04-26T08:30:58.647Z', 1365, 2, 'branch/default', 'success', 734],
            ['2021-04-25T21:06:42.331Z', 1385, 2, 'branch/default', 'success', 733],
            ['2021-04-25T16:21:35.949Z', 1375, 1, 'branch/default', 'success', 732],
            ['2021-04-11T20:39:05.928Z', 1256, 2, 'branch/default', 'success', 707],
            ['2021-04-11T19:54:46.082Z', 1264, 1, 'branch/default', 'success', 705],
            ['2021-04-11T19:30:56.280Z', 1262, 2, 'branch/default', 'success', 704],
            ['2021-04-11T19:00:52.133Z', 1262, 1, 'branch/default', 'success', 703],
            ['2021-04-11T17:00:49.709Z', 1261, 3, 'branch/default', 'success', 702],
            ['2021-04-11T13:33:59.193Z', 1279, 2, 'branch/default', 'success', 701],
            ['2021-04-11T11:20:35.738Z', 3298, 1, 'branch/default', 'success', 700],
            ['2021-04-10T20:49:04.372Z', 6048, 3, 'branch/default', 'success', 696],
            ['2021-04-08T20:48:38.038Z', 436, None, 'branch/default', 'success', 691],
            ['2021-04-08T20:31:35.329Z', 438, 159, 'branch/default', 'success', 690],
            ['2021-04-08T20:23:59.930Z', 393, 220, 'branch/default', 'failed', 689],
            ['2021-04-08T20:21:09.539Z', 387, 1, 'branch/default', 'failed', 688],
            ['2021-04-07T21:18:22.549Z', 438, 1, 'branch/default', 'success', 686],
            ['2021-04-07T21:02:35.363Z', 387, None, 'branch/default', 'failed', 685],
            ['2021-04-07T20:48:10.199Z', 426, 2, 'branch/default', 'failed', 684],
            ['2021-04-07T20:35:34.353Z', 437, 1, 'branch/default', 'success', 683],
            ['2021-04-07T20:15:28.558Z', 501, 2, 'branch/default', 'success', 682],
            ['2021-04-05T17:56:28.524Z', 388, 1, 'branch/default', 'success', 678],
            ['2021-04-05T17:22:43.860Z', 381, 1, 'branch/default', 'failed', 677],
            ['2021-04-05T17:06:05.787Z', 351, 1, 'branch/default', 'failed', 676],
            ['2021-04-05T13:39:41.271Z', 344, 1, 'branch/default', 'success', 673],
            ['2021-03-28T21:14:39.567Z', 336, 1, 'branch/default', 'success', 665],
            ['2021-03-28T20:57:39.418Z', 339, None, 'branch/default', 'success', 663],
            ['2021-03-28T20:42:12.537Z', 332, 3, 'branch/default', 'success', 662],
            ['2021-03-28T20:31:49.798Z', 334, 41, 'branch/default', 'failed', 661],
            ['2021-03-28T20:26:49.221Z', 337, 2, 'branch/default', 'success', 660],
            ['2021-03-28T20:20:45.825Z', 299, 2, 'branch/default', 'success', 659],
            ['2021-03-28T20:11:26.728Z', 303, 2, 'branch/default', 'success', 658],
            ['2021-03-28T19:59:54.535Z', 299, 1, 'branch/default', 'failed', 657],
            ['2021-03-28T19:49:18.585Z', 296, 1, 'branch/default', 'failed', 656],
            ['2021-03-28T11:13:15.793Z', 39, 3, 'branch/default', 'failed', 651],
            ['2021-03-27T21:12:35.950Z', 60, 1, 'branch/default', 'failed', 650],
            ['2021-03-07T10:53:13.292Z', 208, 2, 'branch/default', 'failed', 615],
        ]
        for r in rows:
            yield dict(zip(header, r))

    def test_get_pipeline_runtime_df_empty(self):
        actual = gitlab.get_pipeline_runtime_df(
            self.storage._conn, reference='branch/default', moving_average_window=10
        )
        self.assertEqual(0, len(actual))

    def test_get_pipeline_runtime_df_datetime_range(self):
        self.storage.upsert_res(self.get_pipeline_resources(), self.table)
        actual = gitlab.get_pipeline_runtime_df(
            self.storage._conn,
            reference='branch/default',
            moving_average_window=10,
            after=datetime.fromisoformat('2024-05-09T09:34:32').replace(tzinfo=timezone.utc),
            before=datetime.fromisoformat('2024-06-30T15:14:40').replace(tzinfo=timezone.utc),
        )

        self.assertEqual([
            41167, 41154, 40707, 40705, 40704, 40703, 40702, 40701,
            40700, 40699, 40696, 40695, 40654, 40650, 33006,
        ], list(actual.pipeline_id))
        self.assertEqual([
            1961, 1915, 1995, 1901, 1897, 1895, 1906, 1914, 1915, 2167, 2234, 2256, 2244, 257, 2327
        ], list(actual.duration))
        self.assertEqual([
            pandas.Timestamp('2024-06-26 06:24:44.210000038'),
            pandas.Timestamp('2024-06-25 21:51:45.982000113'),
            pandas.Timestamp('2024-06-23 13:35:02.283999920'),
            pandas.Timestamp('2024-06-23 12:39:04.503999949'),
            pandas.Timestamp('2024-06-23 11:31:21.470999956'),
            pandas.Timestamp('2024-06-23 11:05:09.507999897'),
            pandas.Timestamp('2024-06-23 10:13:52.078999996'),
            pandas.Timestamp('2024-06-23 09:39:38.036000013'),
            pandas.Timestamp('2024-06-23 08:48:47.197999954'),
            pandas.Timestamp('2024-06-23 08:03:38.329999924'),
            pandas.Timestamp('2024-06-22 19:51:17.082999945'),
            pandas.Timestamp('2024-06-22 19:39:04.653000116'),
            pandas.Timestamp('2024-06-21 17:45:54.062000036'),
            pandas.Timestamp('2024-06-21 17:31:05.089999914'),
            pandas.Timestamp('2024-05-09 09:34:32.292000055'),
        ], list(actual.created_at))
        self.assertEqual([
            pandas.Timestamp('1970-01-01 00:32:41'),
            pandas.Timestamp('1970-01-01 00:31:55'),
            pandas.Timestamp('1970-01-01 00:33:15'),
            pandas.Timestamp('1970-01-01 00:31:41'),
            pandas.Timestamp('1970-01-01 00:31:37'),
            pandas.Timestamp('1970-01-01 00:31:35'),
            pandas.Timestamp('1970-01-01 00:31:46'),
            pandas.Timestamp('1970-01-01 00:31:54'),
            pandas.Timestamp('1970-01-01 00:31:55'),
            pandas.Timestamp('1970-01-01 00:36:07'),
            pandas.Timestamp('1970-01-01 00:37:14'),
            pandas.Timestamp('1970-01-01 00:37:36'),
            pandas.Timestamp('1970-01-01 00:37:24'),
            pandas.Timestamp('1970-01-01 00:04:17'),
            pandas.Timestamp('1970-01-01 00:38:47'),
        ], list(actual.duration_delta))
        self.assertEqual([
            pandas.NaT, pandas.NaT, pandas.NaT, pandas.NaT, pandas.NaT,
            pandas.Timestamp('1970-01-01 00:32:26.6'),
            pandas.Timestamp('1970-01-01 00:32:53.9'),
            pandas.Timestamp('1970-01-01 00:33:28'),
            pandas.Timestamp('1970-01-01 00:33:52.9'),
            pandas.Timestamp('1970-01-01 00:31:08.500000'),
            pandas.Timestamp('1970-01-01 00:31:51.500000'),
            pandas.NaT, pandas.NaT, pandas.NaT, pandas.NaT,
        ], list(actual.duration_avg))
        self.assertEqual([
            'success', 'failed', 'success', 'success', 'success', 'success', 'success', 'failed',
            'failed', 'failed', 'success', 'success', 'success', 'failed', 'success',
        ], list(actual.status))
        self.assertEqual(
            [33, 20, 34, 27, 335, 14, 48, 12, 9, 13, 1563, 25, 54, 11, 1],
            list(actual.queued_duration),
        )

    def test_get_pipeline_runtime_df_clamp_range(self):
        self.storage.upsert_res(self.get_pipeline_resources(), self.table)
        actual = gitlab.get_pipeline_runtime_df(
            self.storage._conn,
            reference='branch/default',
            moving_average_window=2,
            clamp_min=1906,
            clamp_max=1914,
        )

        self.assertEqual([40702, 40701, 22680], list(actual.pipeline_id))
        self.assertEqual([1906, 1914, 1910], list(actual.duration))
        self.assertEqual([
            pandas.Timestamp('2024-06-23 10:13:52.078999996'),
            pandas.Timestamp('2024-06-23 09:39:38.036000013'),
            pandas.Timestamp('2024-02-26 22:31:43.085999966'),
        ], list(actual.created_at))
        self.assertEqual([
            pandas.Timestamp('1970-01-01 00:31:46'),
            pandas.Timestamp('1970-01-01 00:31:54'),
            pandas.Timestamp('1970-01-01 00:31:50'),
        ], list(actual.duration_delta))
        self.assertEqual([
            pandas.NaT,
            pandas.Timestamp('1970-01-01 00:31:50'),
            pandas.Timestamp('1970-01-01 00:31:52'),
        ], list(actual.duration_avg))
        self.assertEqual(['success', 'failed', 'success'], list(actual.status))
        self.assertEqual([48, 12, 3], list(actual.queued_duration))

    def test_get_pipeline_runtime_df_all(self):
        self.storage.upsert_res(self.get_pipeline_resources(), self.table)
        actual = gitlab.get_pipeline_runtime_df(
            self.storage._conn,
            reference='1.11.1',
            moving_average_window=1,
        )
        self.assertEqual(
            [(
                0,
                41862,
                pandas.Timestamp('2024-06-30 15:38:52.029000044'),
                983,
                'success',
                645,
                pandas.Timestamp('1970-01-01 00:16:23'),
                pandas.Timestamp('1970-01-01 00:16:23')
            )],
            list(actual.itertuples()),
        )

    def test_plot_pipeline_runtime(self):
        self.storage.upsert_res(self.get_pipeline_resources(), self.table)
        df = gitlab.get_pipeline_runtime_df(
            self.storage._conn,
            reference='branch/default',
            moving_average_window=10,
            after=datetime.fromisoformat('2024-05-09T09:34:32').replace(tzinfo=timezone.utc),
            before=datetime.fromisoformat('2024-06-30T15:14:40').replace(tzinfo=timezone.utc),
            clamp_min=1900,
            clamp_max=2000,
        )
        actual = gitlab.plot_pipeline_runtime(df, title='Test plot')
        self.assertEqual('Test plot', actual.layout.title.text)
        self.assertEqual([
            datetime(2024, 6, 26, 6, 24, 44, 210000),
            datetime(2024, 6, 23, 13, 35, 2, 283999),
            datetime(2024, 6, 23, 12, 39, 4, 503999),
            datetime(2024, 6, 23, 10, 13, 52, 78999),
        ], list(actual.data[0].x))
        self.assertEqual([
            datetime(1970, 1, 1, 0, 32, 41),
            datetime(1970, 1, 1, 0, 33, 15),
            datetime(1970, 1, 1, 0, 31, 41),
            datetime(1970, 1, 1, 0, 31, 46),
        ], list(actual.data[0].y))

    def test_pipeline_runtime_cmd(self):
        with tempfile.NamedTemporaryFile() as db:
            with tempfile.NamedTemporaryFile() as plt:
                with closing(resdb.SqliteStorage(db.name)) as storage:
                    storage.create_res_table(self.table)
                    gitlab.pipeline_runtime_cmd(
                        db.name,
                        plt.name,
                        'branch/default',
                        moving_average_window=10,
                        clamp_min=1900,
                        clamp_max=2000,
                        after=datetime.fromisoformat('2024-05-09T09:34:32+00:00'),
                        before=datetime.fromisoformat('2024-06-30T15:14:40+00:00'),
                    )
                plt.seek(-10000, os.SEEK_END)
                html = plt.read()
        self.assertIn(b'Plotly.newPlot(', html)
        self.assertIn(
            b'Pipeline Runtime for \u003ci\u003ebranch\u002fdefault\u003c\u002fi\u003e', html
        )


class TestUtility(unittest.TestCase):

    def test_chunk_iter(self):
        self.assertEqual([], list(utility.chunk_iter(range(0), 2)))
        self.assertEqual([(0, 1), (2, 3)], list(utility.chunk_iter(range(4), 2)))
        self.assertEqual([(0, 1), (2, 3), (4,)], list(utility.chunk_iter(range(5), 2)))

    def test_partition_pair_iter(self):
        iterable = [('a', 1), ('a', 2), ('b', 1), ('a', 3), ('b', 2)]
        self.assertEqual(
            [('a', (1, 2)), ('b', (1, 2)), ('a', (3,))],
            list(utility.partition_pair_iter(iterable, 2)),
        )

    def test_parse_timestamp(self):
        self.assertEqual(
            datetime(2024, 1, 25, 11, 22, 24, tzinfo=timezone.utc),
            utility.parse_timestamp('2024-01-25T11:22:24.000+00:00'),
        )
        self.assertEqual(
            datetime(2024, 6, 17, 11, 42, 47, 91000, tzinfo=timezone.utc),
            utility.parse_timestamp('2024-06-17T11:42:47.091Z'),
        )


unittest.TestCase.maxDiff = None
