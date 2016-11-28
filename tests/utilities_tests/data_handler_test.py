##############################################################################
# Copyright (c) 2016 EMC and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

import os
import unittest

import mock

from storperf.utilities.data_handler import DataHandler


class MockGraphiteDB(object):

    def __init__(self):
        self.called = False

    def fetch_averages(self, job_id):
        self.called = True
        return None


class DataHandlerTest(unittest.TestCase):

    def setUp(self):
        self.event_listeners = set()
        self.data_handler = DataHandler()
        self._terminated = False
        self.args = None
        self.start_time = 0
        self.end_time = 1
        self.metadata = {}
        self.block_sizes = "1"
        self.queue_depths = "1"
        mock.job_id = "1"
        self.job_db = mock
        self.pushed = False
        pass

    @property
    def terminated(self):
        return self._terminated

    def push_results_to_db(self, *args):
        self.pushed = True
        pass

    def test_not_terminated_report(self):
        self.data_handler.data_event(self)

    @mock.patch.dict(os.environ, {'TEST_DB_URL': 'mock'})
    @mock.patch("storperf.db.test_results_db.push_results_to_db")
    @mock.patch("storperf.utilities.data_handler.GraphiteDB")
    def test_terminated_report(self, mock_graphite_db, mock_results_db):
        self._terminated = True
        mock_results_db.side_effect = self.push_results_to_db
        mock_graphite_db.side_effect = MockGraphiteDB

        self.data_handler.data_event(self)
        self.assertEqual(True, self.pushed)

    @mock.patch.dict(os.environ, {'TEST_DB_URL': 'mock'})
    @mock.patch("storperf.db.test_results_db.push_results_to_db")
    @mock.patch("storperf.utilities.data_handler.GraphiteDB")
    def test_non_terminated_report(self, mock_graphite_db, mock_results_db):
        self._terminated = False
        mock_results_db.side_effect = self.push_results_to_db
        mock_graphite_db.side_effect = MockGraphiteDB

        self.data_handler.data_event(self)
        self.assertEqual(False, self.pushed)
