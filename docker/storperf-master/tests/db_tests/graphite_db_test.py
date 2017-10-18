##############################################################################
# Copyright (c) 2016 EMC and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

import unittest

import mock

from storperf.db.graphite_db import GraphiteDB


class MockResponse():

    def __init__(self):
        self.content = ""
        self.status_code = 200


class GraphiteDBTest(unittest.TestCase):

    def setUp(self):
        self.graphdb = GraphiteDB()
        self.graphdb._job_db = self

    def test_wildcard_pattern(self):
        workload = "job_id"
        expected = "job_id.*.*.*.*.*.*"
        actual = self.graphdb.make_fullname_pattern(workload)
        self.assertEqual(expected, actual, actual)

    def test_no_wildcard_pattern(self):
        workload = "job_id.workload.host.queue-depth.1.block-size.16"
        actual = self.graphdb.make_fullname_pattern(workload)
        self.assertEqual(workload, actual, actual)

    def test_fetch_averages(self):
        # self.graphdb.fetch_averages(u'32d31724-fac1-44f3-9033-ca8e00066a36')
        pass

    @mock.patch("requests.get")
    def test_fetch_series(self, mock_requests):

        response = MockResponse()
        response.content = """
[
    {
        "datapoints": [
            [null,1480455880],
            [null,1480455890],
            [null,1480455900],
            [205.345,1480455910],
            [201.59,1480455920],
            [205.76,1480455930],
            [null,1480455940],
            [null,1480455950],
            [null,1480455960],
            [215.655,1480455970],
            [214.16,1480455980],
            [213.57,1480455990],
            [null,1480456000],
            [null,1480456010],
            [null,1480456020],
            [219.37,1480456030],
            [219.28,1480456040],
            [217.75,1480456050],
            [null,1480456060]
        ],
        "target":"averageSeries(.8192.*.jobs.1.write.iops)"
    }
]"""
        expected = [[1480455910, 205.345],
                    [1480455920, 201.59],
                    [1480455930, 205.76],
                    [1480455970, 215.655],
                    [1480455980, 214.16],
                    [1480455990, 213.57],
                    [1480456030, 219.37],
                    [1480456040, 219.28],
                    [1480456050, 217.75]]

        mock_requests.side_effect = (response,)

        actual = self.graphdb.fetch_series("averageSeries",
                                           "workload", "iops",
                                           "write", 0, 600)
        self.assertEqual(expected, actual)

    def fetch_workloads(self, workload):
        workloads = [[u'32d31724-fac1-44f3-9033-ca8e00066a36.'
                      u'_warm_up.queue-depth.32.block-size.8192.10-9-15-151',
                      u'1462379653', u'1462379893'],
                     [u'32d31724-fac1-44f3-9033-ca8e00066a36.'
                      u'_warm_up.queue-depth.32.block-size.8192.10-9-15-150',
                      u'1462379653', u'1462379898'],
                     [u'32d31724-fac1-44f3-9033-ca8e00066a36'
                      u'.rw.queue-depth.128.block-size.8192.10-9-15-151',
                      u'1462379898', u'1462380028'],
                     [u'32d31724-fac1-44f3-9033-ca8e00066a36'
                      u'.rw.queue-depth.128.block-size.8192.10-9-15-150',
                      u'1462379898', u'1462380032'],
                     [u'32d31724-fac1-44f3-9033-ca8e00066a36'
                      u'.rw.queue-depth.16.block-size.8192.10-9-15-151',
                      u'1462380032', u'1462380312'],
                     [u'32d31724-fac1-44f3-9033-ca8e00066a36'
                      u'.rw.queue-depth.16.block-size.8192.10-9-15-150',
                      u'1462380032', u'1462380329'],
                     ]
        return workloads
