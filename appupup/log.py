# -*- coding: utf-8 -*-
"""
"""
from __future__ import unicode_literals
from __future__ import print_function

import logging
import os


def setup_logging(args, app_name, app_version, app_stage=''):
    """
    Prepares our logging mechanism.

    Examples:

        >>> setup_logging(args, __package_name__, __author__, __version__, 'dev')

    Arguments:
        args:
            Arguments returned by the parser.
        app_name:
            The name of the application.
        app_version:
            The version of the application.
        app_stage:
            Can be dev for development versions or empty for release versions.

    Returns:
        True if all went well, False to exit with error
    """
    logger = logging.getLogger()

    # Determine the level of logging.
    if args.log_level == logging.INFO:
        log_level = logging.DEBUG if args.verbose else logging.INFO
    else:
        try:
            log_level = int(args.log_level)
            if (log_level < 0) or (log_level > logging.CRITICAL):
                raise ValueError
        except ValueError:
            print("ERROR! --log-level expects an integer between 1 and %d" %
                  logging.CRITICAL)
            return False
    args.log_level = log_level

    # The format we're going to use with console output.
    fmt = logging.Formatter(
        "[%(asctime)s] [%(levelname)-7s] [%(name)-19s] [%(threadName)-15s] "
        "[%(funcName)-25s] %(message)s",
        '%M:%S')

    # This is the console output.
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(fmt)
    console_handler.setLevel(log_level)
    logger.addHandler(console_handler)

    # This is the file output.
    if len(args.log_file) > 0 and args.log_file != '-':
        # The format we're going to use with file handler.
        fmt = logging.Formatter(
            "%(asctime)5s [%(levelname)-7s] [%(name)-19s] "
            "[%(filename)15s:%(lineno)-4d] [%(threadName)-15s] "
            "[%(funcName)-25s] | %(message)s",
            '%Y-%m-%d %H:%M:%S')
        file_path, file_name = os.path.split(args.log_file)
        if not os.path.isdir(file_path):
            os.makedirs(file_path)
        file_handler = logging.FileHandler(args.log_file)
        file_handler.setFormatter(fmt)
        file_handler.setLevel(log_level)
        logger.addHandler(file_handler)

    logger.setLevel(log_level)
    logger.info(
        "%s v%s %s STARTED", app_name, app_version, app_stage)
    logger.debug("logging to %s", args.log_file)
    return True
