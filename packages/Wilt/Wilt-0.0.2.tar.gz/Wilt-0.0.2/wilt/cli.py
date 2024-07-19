import argparse
import glob
import importlib
import logging
import sys
from datetime import datetime, timezone
from functools import partial

from . import __version__, utility


logger = logging.getLogger(__package__)


def add_wilt_parser(parent):
    parser = parent.add_parser('cq.wilt', description='Calculate WILT metric.')
    parser.add_argument('files', type=partial(glob_files, parser), help='File, glob or -.')
    parser.add_argument('-i', help='indentation size', dest='indent', type=int, default=4)
    parser.set_defaults(output_file=sys.stdout)


def add_rest_parser(parent):
    rest_parser = parent.add_parser('ci.rest', description='REST tools.')
    rest_parser.add_argument(
        '-r', '--resmap-file',
        help='Resource map file. Default: %(default)s.',
        default='resmapfile.py',
    )
    rest_parser.add_argument(
        '-d', '--database-file',
        help='Target database file. Default: %(default)s.',
        default='ci.sqlite',
    )

    subparent = rest_parser.add_subparsers(dest='subcommand', required=True)

    subparent.add_parser('sync-db', description='Synchronise REST resources.')

    rebuild_parser = subparent.add_parser('rebuild-db', description='Rebuild resource database.')
    rebuild_parser.add_argument('table',  nargs='+', help='Table to rebuild.')


def add_gitlab_parser(parent):
    gl_parser = parent.add_parser('ci.gitlab', description='GitLab tools.')
    gl_parser.add_argument(
        '-d', '--database-file',
        default='ci.sqlite',
        help='Synchronised database file. Default: %(default)s.',
    )
    gl_parser.add_argument(
        '-f', '--plot-file',
        default='plot.html',
        help='Path to the output HTML file. Default: %(default)s.',
    )

    subparent = gl_parser.add_subparsers(dest='subcommand', required=True)

    ppl_plt = subparent.add_parser(
        'pipeline-runtime',
        description='''
            Pipeline runtime plot. Required extract columns: pipeline_id,
            created_at, duration, ref.
        ''',
    )
    ppl_plt.add_argument(
        '-r', '--reference',
        default='master',
        help='Git reference of the pipeline. Default: %(default)s.',
    )
    ppl_plt.add_argument(
        '-a', '--after',
        type=lambda s: datetime.strptime(s, '%Y-%m-%dT%H:%M:%S').replace(tzinfo=timezone.utc),
        help='Include only pipelines after given UTC date, like 2000-01-01T00:00:00.',
    )
    ppl_plt.add_argument(
        '-b', '--before',
        type=lambda s: datetime.strptime(s, '%Y-%m-%dT%H:%M:%S').replace(tzinfo=timezone.utc),
        help='Include only pipelines before given UTC date, like 2000-01-01T00:00:00.',
    )
    ppl_plt.add_argument(
        '--clamp-min',
        type=int,
        help='Clamp minimum runtime, in seconds.',
    )
    ppl_plt.add_argument(
        '--clamp-max',
        type=int,
        help='Clamp maximum runtime, in seconds.',
    )
    ppl_plt.add_argument(
        '-w', '--moving-average-window',
        type=int,
        default='16',
        help='Runtime moving average window size for smoothing. Default: %(default)s.',
    )


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', action='version', version=__version__)
    parser.add_argument(
        '--logging-level',
        help='Logging level. By default: %(default)s.',
        default='INFO',
    )
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output.')

    cmd_funcs = [
        add_wilt_parser,
        add_rest_parser,
        add_gitlab_parser,
    ]
    parent = parser.add_subparsers(dest='command', required=True)
    [fn(parent) for fn in cmd_funcs]

    return parser


def glob_files(parser: argparse.ArgumentParser, files: str) -> str | list[str]:
    if files != '-':
        files = glob.glob(files, recursive=True)
        if not files:
            parser.error('No files found')
    return files


def get_command(cmd_module_name: str, sub_cmd_name: str | None):
    module = importlib.import_module(f'.{cmd_module_name}', __package__)
    fn_name = '{}_cmd'.format(sub_cmd_name.replace('-', '_')) if sub_cmd_name else 'run_cmd'
    return getattr(module, fn_name)


def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)-7s %(name)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

    kwargs = vars(build_parser().parse_args())
    logging.root.setLevel(kwargs.pop('logging_level'))
    try:
        get_command(kwargs.pop('command'), kwargs.pop('subcommand', None))(**kwargs)
    except KeyboardInterrupt:
        pass
    except utility.CommandError as ex:
        logger.error(ex, exc_info=kwargs['verbose'])
        sys.exit(1)
