# -*- coding: utf-8 -*-
"""
"""
from __future__ import unicode_literals
from __future__ import print_function

import logging
import os
import re


# The Pattern was introduced in python 3.7
try:
    _ = re.Pattern

    def is_pattern_object(x):
        return isinstance(x, re.Pattern)

except AttributeError:
    def is_pattern_object(x):
        return type(x).__name__ == 'SRE_Pattern'


def setup_logging(args, app_name, app_version, app_stage='',
                  log_for_console=False):
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
        log_for_console:
            Use a format for stream handler that looks nicer in interactive
            terminals.

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
    if log_for_console:
        fmt = logging.Formatter(
            "%(levelname)s: %(message)s",
            '%M:%S')
    else:
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
    logger.debug(
        "%s v%s %s started", app_name, app_version, app_stage)
    logger.debug("logging to %s", args.log_file)
    return True


class DebugLogger(logging.StreamHandler):
    """
    Logging handler that allows extended filtering of the output.

    One place where you can use this is in a overrides.py that
    is not comited to source control and is loaded by the application
    at startup.

    There are three types of checks for properties of the message:

    * *include*: if the pattern is matched the message will be isued \
      without any other checks. These are checked first.
    * *exclude*: if the pattern is matched the message will NOT be isued \
      and no other checks will be performed. These are checked second.
    * *callback*: if the pattern is matched the callback is called \
      and can decide if it handles the message or not. These are checked last. \
      The callback receives `DebugLogger` as first argument, the \
      formatted message as the second, the value that was \
      matched as the third and the record as fourth. \
      It should call either :meth:~`filtered_in` \
      or :meth:~`filtered_out` if it returns `True`, otherwise it should \
      call neither.
    """
    def __init__(self,
                 include_name_pattern=None, include_thread_pattern=None,
                 include_file_name_pattern=None, include_func_name_pattern=None,
                 include_level_name_pattern=None, include_level_number_pattern=None,
                 include_line_number_pattern=None, include_message_pattern=None,
                 include_module_pattern=None, include_path_pattern=None,
                 include_process_pattern=None,
                 include_created_interval=None, include_relative_created_interval=None,
                 include_level_in=None,
                 exclude_name_pattern=None, exclude_thread_pattern=None,
                 exclude_file_name_pattern=None, exclude_func_name_pattern=None,
                 exclude_level_name_pattern=None, exclude_level_number_pattern=None,
                 exclude_line_number_pattern=None, exclude_message_pattern=None,
                 exclude_module_pattern=None, exclude_path_pattern=None,
                 exclude_process_pattern=None,
                 exclude_created_interval=None, exclude_relative_created_interval=None,
                 exclude_level_in=None,
                 callback_name_pattern=None, callback_thread_pattern=None,
                 callback_file_name_pattern=None, callback_func_name_pattern=None,
                 callback_level_name_pattern=None, callback_level_number_pattern=None,
                 callback_line_number_pattern=None, callback_message_pattern=None,
                 callback_module_pattern=None, callback_path_pattern=None,
                 callback_process_pattern=None,
                 callback_created_interval=None, callback_relative_created_interval=None,
                 callback_level_in=None,
                 ):

        self.include_name_pattern = include_name_pattern
        self.include_thread_pattern = include_thread_pattern
        self.include_file_name_pattern = include_file_name_pattern
        self.include_func_name_pattern = include_func_name_pattern
        self.include_level_name_pattern = include_level_name_pattern
        self.include_level_number_pattern = include_level_number_pattern
        self.include_level_in = include_level_in
        self.include_line_number_pattern = include_line_number_pattern
        self.include_message_pattern = include_message_pattern
        self.include_module_pattern = include_module_pattern
        self.include_path_pattern = include_path_pattern
        self.include_process_pattern = include_process_pattern
        self.include_created_interval = include_created_interval
        self.include_relative_created_interval = include_relative_created_interval

        self.exclude_name_pattern = exclude_name_pattern
        self.exclude_thread_pattern = exclude_thread_pattern
        self.exclude_file_name_pattern = exclude_file_name_pattern
        self.exclude_func_name_pattern = exclude_func_name_pattern
        self.exclude_level_name_pattern = exclude_level_name_pattern
        self.exclude_level_number_pattern = exclude_level_number_pattern
        self.exclude_level_in = exclude_level_in
        self.exclude_line_number_pattern = exclude_line_number_pattern
        self.exclude_message_pattern = exclude_message_pattern
        self.exclude_module_pattern = exclude_module_pattern
        self.exclude_path_pattern = exclude_path_pattern
        self.exclude_process_pattern = exclude_process_pattern
        self.exclude_created_interval = exclude_created_interval
        self.exclude_relative_created_interval = exclude_relative_created_interval

        self.callback_name_pattern = callback_name_pattern
        self.callback_thread_pattern = callback_thread_pattern
        self.callback_file_name_pattern = callback_file_name_pattern
        self.callback_func_name_pattern = callback_func_name_pattern
        self.callback_level_name_pattern = callback_level_name_pattern
        self.callback_level_number_pattern = callback_level_number_pattern
        self.callback_level_in = callback_level_in
        self.callback_line_number_pattern = callback_line_number_pattern
        self.callback_message_pattern = callback_message_pattern
        self.callback_module_pattern = callback_module_pattern
        self.callback_path_pattern = callback_path_pattern
        self.callback_process_pattern = callback_process_pattern
        self.callback_created_interval = callback_created_interval
        self.callback_relative_created_interval = callback_relative_created_interval

        logging.StreamHandler.__init__(self)

    def filter_callback(self, pattern, msg, value, record):
        """ Checks if a value matches the pattern. """
        if pattern is None:
            return True
        pattern, callback = pattern

        if is_pattern_object(pattern):
            if pattern.match(str(value)):
                return callback(self, msg, value, record)
        else:
            if str(pattern) == str(value):
                return callback(self, msg, value, record)
        return True

    def filter_include(self, pattern, value):
        """ Checks if a value matches the pattern. """
        if pattern is None:
            return True
        elif is_pattern_object(pattern):
            return pattern.match(str(value))
        else:
            return str(pattern) == str(value)

    def filter_exclude(self, pattern, value):
        """ Checks if a value matches the pattern. """
        if pattern is None:
            return False
        elif is_pattern_object(pattern):
            return pattern.match(str(value))
        else:
            return str(pattern) == str(value)

    def check_interval_callback(self, interval, msg, value, record, include=True):
        """ Checks if a value is inside a given interval (inclusive). """
        if interval is None:
            return True

        interval, callback = interval
        if include:
            if (value >= interval[0]) and (value <= interval[1]):
                return callback(self, value, record)

        else:
            if (value < interval[0]) or (value > interval[1]):
                return callback(self, msg, value, record)

        return True

    def check_interval(self, interval, value, include=True):
        """ Checks if a value is inside a given interval (inclusive). """
        if interval is None:
            return True
        else:
            if include:
                return (value >= interval[0]) and (value <= interval[1])
            else:
                return (value < interval[0]) or (value > interval[1])

    def check_in_callback(self, acceptable, msg, value, record):
        """ Checks if a value is inside a given interval (inclusive). """
        if acceptable is None:
            return True

        acceptable, callback = acceptable
        if value in acceptable:
            return callback(self, msg, value, record)

        return True

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
            if self.filter_exclude(self.exclude_thread_pattern, record.threadName):
                break
            if self.filter_exclude(self.exclude_name_pattern, record.name):
                break
            if self.filter_exclude(self.exclude_file_name_pattern, record.filename):
                break
            if self.filter_exclude(self.exclude_func_name_pattern, record.funcName):
                break
            if self.filter_exclude(self.exclude_level_name_pattern, record.levelname):
                break
            if self.filter_exclude(self.exclude_level_number_pattern, record.levelno):
                break
            if self.filter_exclude(self.exclude_line_number_pattern, record.lineno):
                break
            if self.filter_exclude(self.exclude_message_pattern, record.message):
                break
            if self.filter_exclude(self.exclude_module_pattern, record.module):
                break
            if self.filter_exclude(self.exclude_path_pattern, record.pathname):
                break
            if self.filter_exclude(self.exclude_process_pattern, record.processName):
                break
            if not self.check_interval(self.exclude_created_interval, record.created):
                break
            if not self.check_interval(self.exclude_relative_created_interval, record.relativeCreated):
                break
            if not self.check_in(self.exclude_level_in, record.levelno):
                break

            if not self.filter_include(self.include_thread_pattern, record.threadName):
                break
            if not self.filter_include(self.include_name_pattern, record.name):
                break
            if not self.filter_include(self.include_file_name_pattern, record.filename):
                break
            if not self.filter_include(self.include_func_name_pattern, record.funcName):
                break
            if not self.filter_include(self.include_level_name_pattern, record.levelname):
                break
            if not self.filter_include(self.include_level_number_pattern, record.levelno):
                break
            if not self.filter_include(self.include_line_number_pattern, record.lineno):
                break
            if not self.filter_include(self.include_message_pattern, record.message):
                break
            if not self.filter_include(self.include_module_pattern, record.module):
                break
            if not self.filter_include(self.include_path_pattern, record.pathname):
                break
            if not self.filter_include(self.include_process_pattern, record.processName):
                break
            if not self.check_interval(self.include_created_interval, record.created):
                break
            if not self.check_interval(self.include_relative_created_interval, record.relativeCreated):
                break
            if not self.check_in(self.include_level_in, record.levelno):
                break


            if not self.filter_callback(self.callback_thread_pattern, msg, record.threadName, record):
                return
            if not self.filter_callback(self.callback_name_pattern, msg, record.name, record):
                return
            if not self.filter_callback(self.callback_file_name_pattern, msg, record.filename, record):
                return
            if not self.filter_callback(self.callback_func_name_pattern, msg, record.funcName, record):
                return
            if not self.filter_callback(self.callback_level_name_pattern, msg, record.levelname, record):
                return
            if not self.filter_callback(self.callback_level_number_pattern, msg, record.levelno, record):
                return
            if not self.filter_callback(self.callback_line_number_pattern, msg, record.lineno, record):
                return
            if not self.filter_callback(self.callback_message_pattern, msg, record.message, record):
                return
            if not self.filter_callback(self.callback_module_pattern, msg, record.module, record):
                return
            if not self.filter_callback(self.callback_path_pattern, msg, record.pathname, record):
                return
            if not self.filter_callback(self.callback_process_pattern, msg, record.processName, record):
                return
            if not self.check_interval_callback(self.callback_created_interval, msg, record.created, record):
                return
            if not self.check_interval_callback(self.callback_relative_created_interval, msg, record.relativeCreated, record):
                return
            if not self.check_in_callback(self.callback_level_in, msg, record.levelno, record):
                return

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
