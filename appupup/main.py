# -*- coding: utf-8 -*-
"""
"""
from __future__ import unicode_literals
from __future__ import print_function

from datetime import datetime
import logging
from random import random
import configparser
import importlib

from appupup.log import setup_logging
from appupup.parse_args import make_argument_parser


def main(app_name, app_version, app_stage, app_author, app_description,
         parser_constructor=None):
    """
    Entry point for the application.
    """
    result = 0
    random.seed(datetime.now())

    # deal with arguments
    parser = make_argument_parser(
        app_author, app_name, app_description,
        parser_constructor=parser_constructor)
    args = parser.parse_args()
    args.parser = parser

    # load configuration
    cfg = configparser.ConfigParser()
    if len(args.config) > 0 and args.config != '-':
        cfg.read(args.config)
    args.cfg = cfg

    # prepare the logger
    logger = logging.getLogger(app_name)
    setup_logging(args, app_name, app_version, app_stage)
    logger.debug("config file is at %s", args.config)

    try:
        func = args.func
    except AttributeError:
        func = None
        parser.print_help()

    # Allow some overrides before starting the app.
    # This would be a python module hidden from the version control used
    # in debugging where you can e.g. filter logging output.
    try:
        # noinspection PyUnresolvedReferences
        overrides = importlib.import_module('.overrides')
        overrides.init(args)
    except ImportError:
        pass

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
