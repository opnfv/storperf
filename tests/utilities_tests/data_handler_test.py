##############################################################################
# Copyright (c) 2016 EMC and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

import os
from storperf.utilities.data_handler import DataHandler
import unittest

import mock


class MockGraphiteDB(object):

    def __init__(self):
        self.called = False
        self.series = []

    def fetch_averages(self, job_id):
        self.called = True
        return None

    def fetch_series(self, job_id, timeframe):
        return self.series


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
        self.current_workload = None
        pass

    @property
    def terminated(self):
        return self._terminated

    def push_results_to_db(self, *args):
        self.pushed = True
        pass

    def terminate(self):
        self._terminated = True

    def terminate_current_run(self):
        self._terminated = True

    @mock.patch("time.time")
    @mock.patch.dict(os.environ, {'TEST_DB_URL': 'mock'})
    @mock.patch("storperf.db.graphite_db.GraphiteDB.fetch_series")
    def test_lookup_prior_data(self, mock_graphite_db, mock_time):
        self._terminated = False
        expected = [[1480455910, 205.345],
                    [1480455920, 201.59],
                    [1480455930, 205.76],
                    [1480455970, 215.655],
                    [1480455980, 214.16],
                    [1480455990, 213.57],
                    [1480456030, 219.37],
                    [1480456040, 219.28],
                    [1480456050, 217.75]]
        mock_graphite_db.return_value = expected
        mock_time.return_value = expected[-1][0] + 10

        self.current_workload = ("%s.%s.queue-depth.%s.block-size.%s" %
                                 ("job_id",
                                  "rw",
                                  8,
                                  8192))

        actual = self.data_handler._lookup_prior_data(self, 'read', 'iops')
        self.assertEqual(expected, actual)

    def test_short_sample(self):
        series = [[1480455910, 205.345],
                  [1480455920, 201.59],
                  [1480455930, 205.76],
                  [1480455970, 215.655],
                  [1480455980, 214.16],
                  [1480455990, 213.57],
                  [1480456030, 219.37],
                  [1480456040, 219.28],
                  [1480456050, 217.75]]

        actual = self.data_handler._evaluate_prior_data(series)
        self.assertEqual(False, actual)

    def test_long_not_steady_sample(self):
        series = [[4804559100, 205345],
                  [4804559200, 20159],
                  [4804559300, 20576],
                  [4804560300, 21937],
                  [4804560400, 21928],
                  [4804560500, 21775]]
        actual = self.data_handler._evaluate_prior_data(series)
        self.assertEqual(False, actual)

    def test_long_steady_sample(self):
        series = [[4804559100, 205.345],
                  [4804559200, 201.59],
                  [4804559300, 205.76],
                  [4804559400, 205.76],
                  [4804559500, 205.76],
                  [4804559600, 205.76],
                  [4804559700, 205.76],
                  [4804560300, 219.37],
                  [4804560400, 219.28],
                  [4804560500, 217.75]]
        actual = self.data_handler._evaluate_prior_data(series)
        self.assertEqual(True, actual)

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
    @mock.patch("time.time")
    @mock.patch("storperf.db.test_results_db.push_results_to_db")
    @mock.patch("storperf.db.graphite_db.GraphiteDB.fetch_series")
    def test_non_terminated_report(self, mock_graphite_db, mock_results_db,
                                   mock_time):
        self._terminated = False
        mock_results_db.side_effect = self.push_results_to_db
        series = \
            [[1480455910, 205.345],
             [1480455920, 201.59],
             [1480455930, 205.76],
             [1480455970, 215.655],
             [1480455980, 214.16],
             [1480455990, 213.57],
             [1480456030, 219.37],
             [1480456040, 219.28],
             [1480456050, 217.75]]
        mock_graphite_db.return_value = series
        mock_time.return_value = series[-1][0] + 10
        expected_slope = 0.1185333530108134
        expected_range = 17.78
        expected_average = 212.49777777777774

        self.current_workload = ("%s.%s.queue-depth.%s.block-size.%s" %
                                 ("job_id",
                                  "rw",
                                  8,
                                  8192))

        self.data_handler.data_event(self)
        self.assertEqual(False, self.pushed)
        self.assertEqual(False, self._terminated)

        self.assertEqual(expected_slope, self.metadata['report_data']
                         ['rw.queue-depth.8.block-size.8192']
                         ['lat.mean']
                         ['read']
                         ['slope'])
        self.assertEqual(expected_range, self.metadata['report_data']
                         ['rw.queue-depth.8.block-size.8192']
                         ['lat.mean']
                         ['read']
                         ['range'])
        self.assertEqual(expected_average, self.metadata['report_data']
                         ['rw.queue-depth.8.block-size.8192']
                         ['lat.mean']
                         ['read']
                         ['average'])
        self.assertEqual(series, self.metadata['report_data']
                         ['rw.queue-depth.8.block-size.8192']
                         ['lat.mean']
                         ['read']
                         ['series'])

    @mock.patch.dict(os.environ, {'TEST_DB_URL': 'mock'})
    @mock.patch("time.time")
    @mock.patch("storperf.db.test_results_db.push_results_to_db")
    @mock.patch("storperf.db.graphite_db.GraphiteDB.fetch_series")
    def test_report_that_causes_termination(self,
                                            mock_graphite_db,
                                            mock_results_db,
                                            mock_time):
        self._terminated = False
        mock_results_db.side_effect = self.push_results_to_db
        series = [[4804559100, 205.345],
                  [4804559200, 201.59],
                  [4804559300, 205.76],
                  [4804559400, 205.76],
                  [4804559500, 205.76],
                  [4804559600, 205.76],
                  [4804559700, 205.76],
                  [4804560300, 219.37],
                  [4804560400, 219.28],
                  [4804560500, 217.75]]
        mock_graphite_db.return_value = series
        mock_time.return_value = 4804560500 + 10

        expected_slope = 0.01266822319352225
        expected_range = 17.78
        expected_average = 209.2135

        self.current_workload = ("%s.%s.queue-depth.%s.block-size.%s" %
                                 ("job_id",
                                  "rw",
                                  8,
                                  8192))

        self.data_handler.data_event(self)

        self.assertEqual(expected_slope, self.metadata['report_data']
                         ['rw.queue-depth.8.block-size.8192']
                         ['lat.mean']
                         ['read']
                         ['slope'])
        self.assertEqual(expected_range, self.metadata['report_data']
                         ['rw.queue-depth.8.block-size.8192']
                         ['lat.mean']
                         ['read']
                         ['range'])
        self.assertEqual(expected_average, self.metadata['report_data']
                         ['rw.queue-depth.8.block-size.8192']
                         ['lat.mean']
                         ['read']
                         ['average'])
        self.assertEqual(series, self.metadata['report_data']
                         ['rw.queue-depth.8.block-size.8192']
                         ['lat.mean']
                         ['read']
                         ['series'])
        self.assertEqual(True, self._terminated)

        self.assertEqual(False, self.pushed)
