# -*- coding: utf-8 -*-
"""
"""
from __future__ import unicode_literals
from __future__ import print_function

import logging
import os
from appdirs import user_config_dir

logger = logging.getLogger('appupup')


def get_config_file(app_name, app_author, args=None):
    """
    Get the path to config file.

    Examples:

        >>> get_config_file(__package_name__, __author__, args)

    Arguments:
        app_name:
            The name of the application.
        app_author:
            The author of the application.
        args:
            Parsed arguments.
    """
    if args is not None:
        if len(args.config) > 0 and args.config != '-':
            return args.config
    ucd = user_config_dir(app_name, app_author)
    if not os.path.isdir(ucd):
        os.makedirs(ucd)
    return os.path.join(ucd, '%s.cfg' % app_name)
