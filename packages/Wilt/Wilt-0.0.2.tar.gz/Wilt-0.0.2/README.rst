.. image:: https://img.shields.io/pypi/l/Wilt.svg
   :target: https://spdx.org/licenses/GPL-3.0-or-later.html
   :alt: PyPI - License
.. image:: https://heptapod.host/saajns/wilt/badges/branch/default/pipeline.svg
   :target: https://heptapod.host/saajns/wilt/-/commits/branch/default
   :alt: Pipeline status
.. image:: https://heptapod.host/saajns/wilt/badges/branch/default/coverage.svg
   :target: https://heptapod.host/saajns/wilt/-/commits/branch/default
   :alt: Test code coverage
.. image:: https://badge.fury.io/py/Wilt.svg
   :target: https://pypi.python.org/pypi/Wilt
   :alt: PyPI

****
Wilt
****
Wilt is an architect's collection of codebase health probes. The name of the
package is inspired by the simplest possible code metric::

   W Whitespace
   I Integrated over
   L Lines of
   T Text

It comes from a great talk by Robert Smallshire called Confronting Complexity
[1]_ [2]_. In the talk there are a few other ideas for codebase health analysis
and visualisation that inspire development of this package.

Install with::

   pipx install Wilt

Code quality
============
Wilt
----
An implementation of WILT itself. The metric can be calculated like::

  $ wilt cq.wilt /usr/lib/python3.12/unittest/case.py
  2677.75

  $ wilt cq.wilt '/usr/lib/python3.12/**/*.py'
  346219.0

  $ echo "    foo" | wilt cq.wilt -i 2 -
  2.0

Continuous integration
======================
REST HTTP API resource synchronisation
--------------------------------------
This feature allows synchronising collections of CI HTTP API resources in a
SQLite database for analysis in SQL. The main use case is GitLab CI
pipelines. Create a file called ``resmapfile.py`` like the following:

.. code:: python

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
               resource_id_key='id',
               resource_timestamp_key='created_at',
           ),
           rm.TargetTable(
               'job',
               extract_columns=[
                   rm.ExtractColumn(
                       'id', rm.ColumnType.integer, name='job_id', pk=True
                   ),
                   rm.ExtractColumn('name', rm.ColumnType.text),
                   rm.ExtractColumn('created_at', rm.ColumnType.datetime),
                   rm.ExtractColumn('duration', rm.ColumnType.numeric),
                   rm.ExtractColumn('status', rm.ColumnType.text),
                   rm.ExtractColumn('pipeline.id', rm.ColumnType.integer),
               ],
           ),
           load_interval=rm.timedelta(days=2 * 365),
           sync_lookbehind=rm.timedelta(hours=6),
       ),
   ]

Then run ``wilt -v ci.rest sync-db`` to create and then synchronise a SQLite
database with the HTTP API resources according to the mapping.

.. note::

   Each table is expected to have ``{table_name}_id`` and ``created_at``
   columns.

GitLab CI visualisation
-----------------------
Assuming the following pipeline synchronisation:

.. code:: python

   resources = [
       rm.Resmap(
           rm.SourceResourceCollection(
               '/pipelines',
               request_params={'per_page': 10, 'sort': 'desc'},
               page_size=10,
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
                           rm.ExtractColumn('duration', rm.ColumnType.numeric),
                           rm.ExtractColumn('ref', rm.ColumnType.text),
                       ],
                   ),
               ),
           ],
       ),
   ]

the pipeline runtime can be visualised with a command like::

   wilt ci.gitlab pipeline-runtime --clamp-max 3600 --after 2023-01-01T00:00:00

This produces ``plot.html`` file with interactive Plotly visualisation. See
``wilt ci.gitlab pipeline-runtime --help`` for more details.

____

.. [1] https://www.youtube.com/watch?v=W44Ub5ykBY4
.. [2] https://web.archive.org/web/20170331000730/http://ticosa.org/output/Robert%20Smallshire-Confronting%20Complexity-%20TICOSA%202014.pdf
