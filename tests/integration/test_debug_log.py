# -*- coding: utf-8 -*-
"""
Unit tests for DebugLogger.
"""
from __future__ import unicode_literals
from __future__ import print_function

import logging
import os
import re
import shutil
import tempfile
from unittest import TestCase, SkipTest
from unittest.mock import MagicMock

from appupup.log import DebugLogger

LOGGER = logging.getLogger('tests.appupup.log')


class TestTestee(TestCase):
    def do_me_one(self, *args, **kwargs):
        self.testee = DebugLogger(*args, **kwargs)
        self.testee.filtered_in = MagicMock()
        self.testee.filtered_out = MagicMock()
        self.logger = logging.getLogger('DebugLogger')
        self.logger.handlers = []
        self.logger.addHandler(self.testee)

    def setUp(self):
        pass

    def tearDown(self):
        self.testee = None
        self.logger.handlers = []

    def test_init_all_goes(self):
        self.do_me_one()
        self.logger.debug("test")
        self.testee.filtered_in.assert_called_once()
        self.testee.filtered_out.assert_not_called()

    def test_name_pattern(self):
        self.do_me_one(name_pattern='Other name')
        self.logger.debug("test")
        self.testee.filtered_in.assert_not_called()
        self.testee.filtered_out.assert_called_once()

        self.do_me_one(name_pattern='DebugLogger')
        self.logger.debug("test")
        self.testee.filtered_in.assert_called_once()
        self.testee.filtered_out.assert_not_called()

        self.do_me_one(name_pattern=re.compile('O.+e'))
        self.logger.debug("test")
        self.testee.filtered_in.assert_not_called()
        self.testee.filtered_out.assert_called_once()

        self.do_me_one(name_pattern=re.compile('D.+r'))
        self.logger.debug("test")
        self.testee.filtered_in.assert_called_once()
        self.testee.filtered_out.assert_not_called()

