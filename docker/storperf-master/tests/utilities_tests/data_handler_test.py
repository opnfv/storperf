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
        self.series = []

    def fetch_series(self, job_id, timeframe):
        return self.series


class DataHandlerTest(unittest.TestCase):

    def setUp(self):
        self.event_listeners = set()
        self.data_handler = DataHandler()
        self._terminated = False
        self.args = None
        self.start_time = 0
        self.steady_state_samples = 10
        self.end_time = 1
        self.metadata = {}
        self.metadata['details'] = {}
        self.metadata['details']['metrics'] = {}
        self.block_sizes = "1"
        self.queue_depths = "1"
        mock.job_id = "1"
        self.job_db = mock
        self.pushed = False
        self.current_workload = None
        self.db_results = None
        pass

    @property
    def terminated(self):
        return self._terminated

    def push_results_to_db(self, *args):
        self.pushed = True
        self.db_results = args
        results = {"href": "http://localhost/api/result/uuid-that-is-long"}
        return results

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

        self.current_workload = ("%s.%s.queue-depth.%s.block-size.%s"
                                 % ("job_id",
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

        actual = self.data_handler._evaluate_prior_data(
            series, self.steady_state_samples)
        self.assertEqual(False, actual)

    def test_long_not_steady_sample(self):
        series = [[4804559100, 205345],
                  [4804559200, 20159],
                  [4804559300, 20576],
                  [4804560300, 21937],
                  [4804560400, 21928],
                  [4804560500, 21775]]
        actual = self.data_handler._evaluate_prior_data(
            series, self.steady_state_samples)
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
        actual = self.data_handler._evaluate_prior_data(
            series, self.steady_state_samples)
        self.assertEqual(True, actual)

    @mock.patch.dict(os.environ, {'TEST_DB_URL': 'mock'})
    @mock.patch("storperf.db.test_results_db.push_results_to_db")
    @mock.patch("storperf.utilities.data_handler.GraphiteDB")
    def test_terminated_report(self, mock_graphite_db, mock_results_db):
        self._terminated = True
        mock_results_db.side_effect = self.push_results_to_db
        mock_graphite_db.side_effect = MockGraphiteDB
        self.metadata['details'] = {
            "steady_state": {
                "rr.queue-depth.8.block-size.16384": True,
                "rr.queue-depth.8.block-size.2048": False,
                "rr.queue-depth.8.block-size.8192": True,
            },
        }

        self.data_handler.data_event(self)
        self.assertEqual(True, self.pushed)

    @mock.patch.dict(os.environ, {'TEST_DB_URL': 'mock'})
    @mock.patch("time.time")
    @mock.patch("storperf.db.test_results_db.push_results_to_db")
    @mock.patch("storperf.db.graphite_db.GraphiteDB.fetch_series")
    @mock.patch("storperf.db.job_db.JobDB.fetch_workloads")
    def test_non_terminated_report(self, mock_job_db,
                                   mock_graphite_db,
                                   mock_results_db, mock_time):
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
        expected_slope = 12.292030334472656
        expected_range = 17.78
        expected_average = 212.49777777777774

        self.current_workload = ("%s.%s.queue-depth.%s.block-size.%s"
                                 % ("job_id",
                                    "rw",
                                    8,
                                    8192))
        mock_job_db.return_value = [[self.current_workload, 4804559000, None]]

        self.data_handler.data_event(self)
        self.assertEqual(False, self.pushed)
        self.assertEqual(False, self._terminated)

        self.assertEqual(expected_slope, self.metadata['details']
                         ['report_data']
                         ['rw.queue-depth.8.block-size.8192']
                         ['lat_ns.mean']
                         ['read']
                         ['slope'])
        self.assertEqual(expected_range, self.metadata['details']
                         ['report_data']
                         ['rw.queue-depth.8.block-size.8192']
                         ['lat_ns.mean']
                         ['read']
                         ['range'])
        self.assertEqual(expected_average, self.metadata['details']
                         ['report_data']
                         ['rw.queue-depth.8.block-size.8192']
                         ['lat_ns.mean']
                         ['read']
                         ['average'])

    @mock.patch.dict(os.environ, {'TEST_DB_URL': 'mock'})
    @mock.patch("time.time")
    @mock.patch("storperf.db.test_results_db.push_results_to_db")
    @mock.patch("storperf.db.graphite_db.GraphiteDB.fetch_series")
    @mock.patch("storperf.db.job_db.JobDB.fetch_workloads")
    def test_report_that_causes_termination(self,
                                            mock_job_db,
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
        report_data = [[2, 205.345],
                       [3, 201.59],
                       [5, 205.76],
                       [7, 205.76],
                       [8, 205.76],
                       [10, 205.76],
                       [12, 205.76],
                       [22, 219.37],
                       [23, 219.28],
                       [25, 217.75]]
        mock_graphite_db.return_value = series
        mock_time.return_value = 4804560500 + 10

        expected_slope = 0.7419522662249607
        expected_range = 17.78
        expected_average = 209.2135

        self.current_workload = ("%s.%s.queue-depth.%s.block-size.%s"
                                 % ("job_id",
                                    "rw",
                                    8,
                                    8192))
        mock_job_db.return_value = [[self.current_workload, 4804559000, None]]

        self.data_handler.data_event(self)

        self.assertEqual(expected_slope, self.metadata['details']
                         ['report_data']
                         ['rw.queue-depth.8.block-size.8192']
                         ['lat_ns.mean']
                         ['read']
                         ['slope'])
        self.assertEqual(expected_range, self.metadata['details']
                         ['report_data']
                         ['rw.queue-depth.8.block-size.8192']
                         ['lat_ns.mean']
                         ['read']
                         ['range'])
        self.assertEqual(expected_average, self.metadata['details']
                         ['report_data']
                         ['rw.queue-depth.8.block-size.8192']
                         ['lat_ns.mean']
                         ['read']
                         ['average'])
        self.assertEqual(report_data, self.metadata['details']
                         ['report_data']
                         ['rw.queue-depth.8.block-size.8192']
                         ['lat_ns.mean']
                         ['read']
                         ['series'])
        self.assertEqual(True, self._terminated)

        self.assertEqual(False, self.pushed)

    @mock.patch.dict(os.environ, {'TEST_DB_URL': 'mock'})
    @mock.patch("storperf.db.test_results_db.push_results_to_db")
    def test_playload_report(self,
                             mock_results_db):
        mock_results_db.side_effect = self.push_results_to_db
        self.start_time = 1504559100
        self.end_time = 1504560000
        self.metadata['details'] = {
            "scenario_name": "ceph_ws,wr,rs,rr,rw",
            "status": "OK",
            "steady_state": {
                "rr.queue-depth.8.block-size.16384": True,
                "rr.queue-depth.8.block-size.2048": False,
                "rr.queue-depth.8.block-size.8192": True,
            },
            "storage_node_count": 5,
            "volume_size": 10
        }
        self.data_handler._push_to_db(self)
        self.assertEqual('FAIL', self.db_results[1]['criteria'],
                         'Expected FAIL in criteria')
        self.assertEqual('2017-09-04 21:05:00',
                         self.db_results[1]['start_time'],
                         'Start time')
        self.assertEqual('2017-09-04 21:20:00',
                         self.db_results[1]['end_time'],
                         'End time')
