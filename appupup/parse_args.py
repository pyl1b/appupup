# -*- coding: utf-8 -*-
"""
"""
from __future__ import unicode_literals
from __future__ import print_function

import logging
import argparse
import os

from appdirs import user_log_dir, user_data_dir

from appupup.configure import get_config_file

logger = logging.getLogger('appupup')


def make_argument_parser(app_author, app_name, app_description, app_url,
                         parser_constructor=None):
    """
    Creates an ArgumentParser to read the options for this script from
    sys.argv.

    Examples:

        >>> make_argument_parser(
        ...     __author__, __package_name__, __package_url__,
        ...     "description", parser_constructor=None)

    Arguments:
        app_author:
            The author of the application.
        app_name:
            The name of the application.
        app_description:
            A short description of the application.
        parser_constructor:
            A callable that receives the parser for further construction.
    """

    udd = user_data_dir(app_name, app_author)

    parser = argparse.ArgumentParser(
        description='ko server.',
        epilog="See %s for more information" % app_url,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser = argparse.ArgumentParser(
        description=app_description)
    parser.add_argument(
        '--config', default=get_config_file(app_name, app_author),
        metavar='file', dest='config_file',
        help='specify the location of the config file')
    parser.add_argument(
        "--verbose", default=False,
        action="store_true",
        help="increase output verbosity; equivalent to --log-level=10")
    parser.add_argument(
        "--log-level", default=logging.INFO, type=int,
        metavar="level", action="store",
        help="finer control of verbosity (0 to 50); see also --debug")
    parser.add_argument(
        '--log-file',
        metavar="file", action='store',
        default=os.path.join(
            user_log_dir(app_name, app_author),
            '%s.log' % app_name),
        help='where to save the log; a single - will disable it.')
    parser.add_argument(
        "--version", default=False,
        action="store_true",
        help="print program version and exit")
    parser.add_argument(
        "--hookup", default=False,
        action="store_true",
        help="loads the hook file (default one or specified in hook-file "
             "argument")
    parser.add_argument(
        '--hook-file',
        metavar="file", action='store',
        default=None,
        help='hook file; if not provided a file with the name overrides.py '
             'will be searched for')
    parser.add_argument(
        '--udd',
        action='store', default=udd,
        help='User data directory.')

    if parser_constructor is not None:
        parser_constructor(parser)

    return parser
