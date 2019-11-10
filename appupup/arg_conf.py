# -*- coding: utf-8 -*-
"""
Functionality that combines arguments and configuration files.
"""
from __future__ import unicode_literals
from __future__ import print_function

import logging

logging = logging.getLogger('appupup')


def get_common_arg(args, arg_name, cfg_group, cfg_key, default=None):
    """ Retrieve a setting either from command line or from settings file. """
    result = getattr(args, arg_name)
    if result is None:
        try:
            result = args.cfg[cfg_group][cfg_key]
        except KeyError:
            if default is None:
                raise RuntimeError(
                    "%s needs to be specified either \n"
                    "  at command line as --%s=value or\n"
                    "  in config file as %s=value in [%s] section" %
                    (arg_name, arg_name, cfg_key, cfg_group))
            else:
                result = default
    return result
