import logging
from os import getcwd
from os.path import exists, join
from typing import Dict, Optional, Tuple  # for type hinting

from byteblower_test_framework.logging import configure_logging

from .airtime_fairness import run
from .definitions import LOGGING_PREFIX

try:
    import simplejson as json
except ImportError:
    import json


def main():

    logging.basicConfig(level=logging.INFO)
    configure_logging()

    logging.info('%sPreparing', LOGGING_PREFIX)
    # Load test configuration
    config_file_name, report_path, report_prefix = _parse_arguments()
    test_config = _load_config_file(config_file_name)
    run(test_config, report_path, report_prefix)


def _parse_arguments() -> Tuple[str, Optional[str], str]:
    from argparse import ArgumentParser

    file_base_name = __package__.rsplit('.', maxsplit=1)[-1]
    default_config_file = file_base_name + '.json'

    # By default, look for the configuration files in the current directory:
    default_config_path = '.'

    # 3. Search for the file in the shared test-cases configurations.
    # default_config_path = join('test-configuration', 'test-cases')
    default_report_path = None
    default_report_prefix = 'report'
    parser = ArgumentParser(
        description='ByteBlower TR-398 Airtime Fairness Test case')
    parser.add_argument(
        '--config-file',
        help='Test configuration file to load. If an absolute path is given'
        ', the `<config_path>` won\'t be used.'
        f' Default: {default_config_file!r}',
        default=default_config_file,
        metavar='<config_file>'
    )
    parser.add_argument(
        '--config-path',
        help='Location of the configuration file(s).'
        f' Default: {default_config_path!r}',
        default=default_config_path,
        metavar='<config_path>'
    )
    parser.add_argument(
        '--report-path',
        help='Output location for the report file(s).'
        f' Default: {default_report_path!r} (current directory)',
        default=default_report_path,
        metavar='<report_path>'
    )
    parser.add_argument(
        '--report-prefix',
        help='Prefix for the report file(s).'
        f' Default: {default_report_prefix!r}',
        default=default_report_prefix,
        metavar='<report_prefix>'
    )
    args = parser.parse_args()

    # No need to check ``isabs(args.config_file)`` ourselves.
    # From ``join`` documentation:
    #     If any component is an absolute path, all
    #     previous path components will be discarded.
    config_file_name = join(args.config_path, args.config_file)

    report_path = args.report_path
    if report_path is not None:
        # No need to check ``isabs(args.output_dir)`` ourselves.
        # From ``join`` documentation:
        #     If any component is an absolute path, all
        #     previous path components will be discarded.
        report_path = join(getcwd(), report_path)
    report_prefix = args.report_prefix

    # Sanity checks
    if not exists(config_file_name):
        raise ValueError(
            'Test configuration file does not exist.'
            f' Tried {config_file_name!r}'
        )
    if report_path is not None and not exists(report_path):
        raise ValueError(
            f'Test report path {report_path!r} does not exist.'
            ' Please create the report output location and try again.'
        )

    return config_file_name, report_path, report_prefix


def _load_config_file(config_file_name: str) -> Dict:
    logging.info(
        '%sLoading configuration file %s', LOGGING_PREFIX, config_file_name
    )
    with open(config_file_name, 'r') as config_file:
        test_config = json.load(config_file)
    return test_config
