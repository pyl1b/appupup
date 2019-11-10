# -*- coding: utf-8 -*-
"""
Unit tests for TestDebugLogger.
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

logger = logging.getLogger('tests.log')


class TestTestee(TestCase):
    def setUp(self):
        self.testee = DebugLogger()

    def tearDown(self):
        self.testee = None

    def test_init(self):
        self.testee = DebugLogger()

    def test_check_one(self):
        self.assertTrue(self.testee.check_one(None, 1))
        self.assertFalse(self.testee.check_one(
            re.compile('d'), 1))
        self.assertFalse(self.testee.check_one(
            'd', 1))
        self.assertTrue(self.testee.check_one(
            re.compile('[0-9]+'), 112233))
        self.assertFalse(self.testee.check_one(
            re.compile('[0-9]+'), 'abcd'))
        self.assertTrue(self.testee.check_one(
            re.compile('1'), 1))
        self.assertTrue(self.testee.check_one(
            '1', 1))

    def test_check_interval(self):
        self.assertTrue(self.testee.check_interval(None, 1))
        self.assertTrue(self.testee.check_interval((1, 2), 1))
        self.assertFalse(self.testee.check_interval((1, 2), 10))
        self.assertFalse(self.testee.check_interval((1, 2), 0))
