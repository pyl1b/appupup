# -*- coding: utf-8 -*-
"""
"""
from __future__ import unicode_literals
from __future__ import print_function

import os
from datetime import datetime
import logging
import random
import configparser
import importlib
import importlib.util

from appupup.log import setup_logging
from appupup.parse_args import make_argument_parser


def overrides_file(base_package, args):
    """ Find the location of the hook. """
    while True:

        result = args.hook_file
        if result is not None:
            break

        result = os.path.abspath(
            os.path.join(base_package, 'overrides.py'))
        if os.path.exists(result):
            break

        result = os.path.abspath('overrides.py')
        if os.path.exists(result):
            break

        result = os.path.abspath(
            os.path.join(os.pardir.base_package, 'overrides.py'))
        if os.path.exists(result):
            break

        result = None
        break

    return result


def main(app_name, app_version, app_stage, app_author, app_description,
         app_url, parser_constructor=None, pre_hook=None, base_package=None):
    """
    Entry point for the application.

    Example:

        >>> if __name__ == '__main__':
        >>>     import sys
        >>>     sys.exit(main(
        ...          app_name=__package_name__, app_version=__version__,
        ...          app_stage='',
        ...          app_author=__author__, app_description='something.',
        ...          app_url=__package_url__,
        ...          parser_constructor=create_subparsers))

    Arguments:
        app_name (str):
            The name of the application.
        app_version (str):
            The version of the application (x.y.z).
        app_stage (str):
            Application stage.
        app_author (str):
            The name of the author.
        app_description (str):
            A description to use with the parser.
        app_url (str):
            Application url. Will be part of the epilog.
        parser_constructor (func):
            Optional constructor that can add parser options.
        pre_hook (func):
            Function executed before the function decided by the
            arguments is executed.
        base_package (str):
            The name of the package. Can be used to detect the location of the
            overrides file when the user does not provide one. By default
            this is the same as app_name.

    Returns:
        * 0 for normal exit
        * 1 for exit with error
        * -2 if an unhandled exception was triggered by the main function.
    """
    random.seed(datetime.now())

    if base_package is None:
        base_package = app_name

    # deal with arguments
    parser = make_argument_parser(
        app_author=app_author, app_name=app_name,
        app_description=app_description,
        parser_constructor=parser_constructor,
        app_url=app_url)
    args = parser.parse_args()
    args.parser = parser

    # load configuration
    cfg = configparser.ConfigParser()
    if len(args.config_file) > 0 and args.config_file != '-':
        cfg.read(args.config_file)
    args.cfg = cfg

    # prepare the logger
    logger = logging.getLogger(app_name)
    setup_logging(args, app_name, app_version, app_stage)

    logger.debug("config file is at %s", args.config_file)

    try:
        func = args.func
    except AttributeError:
        func = None
        parser.print_help()

    # Allow some overrides before starting the app.
    # This would be a python module hidden from the version control used
    # in debugging where you can e.g. filter logging output.
    hook_file = overrides_file(base_package=base_package, args=args)
    if hook_file:
        spec = importlib.util.spec_from_file_location(
            "overrides", hook_file)
        hook = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(hook)
            hook.init(args)
        except ImportError:
            pass
    else:
        logger.debug("No hook file was loaded")

    if pre_hook:
        pre_hook(args)

    # noinspection PyBroadException
    try:
        result = func(args, logger) if func is not None else 0
        if not isinstance(result, int):
            if isinstance(result, bool):
                result = 0 if result else 1
            elif isinstance(result, str):
                result = 0 if len(result) > 0 else 1
            else:
                result = 0
    except Exception:
        logger.critical('Fatal error', exc_info=True)
        result = -2
    return result
