# -*- coding: utf-8 -*-
"""
"""
from __future__ import unicode_literals
from __future__ import print_function

import logging
import os
import re


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


class DebugLogger(logging.StreamHandler):
    """
    Logging handler that allows extended filtering of the output.

    One place where you can use this is in a overrides.py that
    is not commited to source control and is loaded by the application
    at startup.
    """
    def __init__(self,
                 name_pattern=None, thread_pattern=None,
                 file_name_pattern=None, func_name_pattern=None,
                 level_name_pattern=None, level_number_pattern=None,
                 line_number_pattern=None, message_pattern=None,
                 module_pattern=None, path_pattern=None,
                 process_pattern=None,
                 created_interval=None, relative_created_interval=None,
                 level_in=None):

        self.name_pattern = name_pattern
        self.thread_pattern = thread_pattern
        self.file_name_pattern = file_name_pattern
        self.func_name_pattern = func_name_pattern
        self.level_name_pattern = level_name_pattern
        self.level_number_pattern = level_number_pattern
        self.level_in = level_in
        self.line_number_pattern = line_number_pattern
        self.message_pattern = message_pattern
        self.module_pattern = module_pattern
        self.path_pattern = path_pattern
        self.process_pattern = process_pattern
        self.created_interval = created_interval
        self.relative_created_interval = relative_created_interval

        logging.StreamHandler.__init__(self)

    def check_one(self, pattern, value):
        """ Checks if a value matches the pattern. """
        if pattern is None:
            return True
        elif isinstance(pattern, re.Pattern):
            return pattern.match(str(value))
        else:
            return str(pattern) == str(value)

    def check_interval(self, interval, value):
        """ Checks if a value is inside a given interval (inclusive). """
        if interval is None:
            return True
        else:
            return (value >= interval[0]) and (value <= interval[0])

    def check_in(self, acceptable, value):
        """ Checks if a value is inside a given interval (inclusive). """
        if acceptable is None:
            return True
        else:
            return value in acceptable

    def filtered_in(self, msg, record):
        """ The function receives messages that were filtered in. """
        super().emit(record)

    def filtered_out(self, msg, record):
        """ The function receives messages that were filtered out. """
        pass

    def emit(self, record):
        """ Reimplemented method to filter messages. """
        msg = self.format(record)
        while True:
            if not self.check_one(self.thread_pattern, record.threadName):
                break
            if not self.check_one(self.name_pattern, record.name):
                break
            if not self.check_one(self.file_name_pattern, record.filename):
                break
            if not self.check_one(self.func_name_pattern, record.funcName):
                break
            if not self.check_one(self.level_name_pattern, record.levelname):
                break
            if not self.check_one(self.level_number_pattern, record.levelno):
                break
            if not self.check_one(self.line_number_pattern, record.lineno):
                break
            if not self.check_one(self.message_pattern, record.message):
                break
            if not self.check_one(self.module_pattern, record.module):
                break
            if not self.check_one(self.path_pattern, record.pathname):
                break
            if not self.check_one(self.process_pattern, record.processName):
                break
            if not self.check_interval(self.created_interval, record.created):
                break
            if not self.check_interval(self.relative_created_interval, record.relativeCreated):
                break
            if not self.check_in(self.level_in, record.levelno):
                break

            self.filtered_in(msg, record)
            return

        self.filtered_out(msg, record)

    @staticmethod
    def install(logger_name=None, exclusive=False, fmt=None, *args, **kwargs):
        """
        Creates the handler and installs it to a logger.

        Arguments:
            logger_name (str):
                The name of the logger where we want to install the handler.
                Can be None to install at the very top.
            exclusive (bool):
                If true will remove all other handlers
            fmt (logging.Formatter):
                The format to be used with the logger.

        Return:
            Newly created handler.
        """

        logger = logging.getLogger(name=logger_name)

        if exclusive:
            logger.handlers = []

        if fmt is None:
            fmt = logging.Formatter(
                "[%(asctime)s.%(msecs)03d] [%(levelname)-7s] [%(name)-19s] "
                "[%(threadName)-15s] "
                "[%(funcName)-25s] %(message)s",
                datefmt='%M:%S')
        result = DebugLogger(*args, **kwargs)
        result.setFormatter(fmt)
        logger.setLevel(1)

        logger.addHandler(result)
        logger.setLevel(1)

        return result
