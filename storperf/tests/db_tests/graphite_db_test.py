from storperf.db.graphite_db import GraphiteDB
import this
import unittest


class GraphiteDBTest(unittest.TestCase):

    def setUp(self):
        self.graphdb = GraphiteDB()
        self.graphdb._job_db = self

    def test_wilcard_pattern(self):
        workload = "job_id"
        expected = "job_id.*.*.*.*.*.*"
        actual = self.graphdb.make_fullname_pattern(workload)
        self.assertEqual(expected, actual, actual)

    def test_no_wilcard_pattern(self):
        workload = "job_id.workload.host.queue-depth.1.block-size.16"
        actual = self.graphdb.make_fullname_pattern(workload)
        self.assertEqual(workload, actual, actual)

    def test_fetch_averages(self):
        # self.graphdb.fetch_averages(u'32d31724-fac1-44f3-9033-ca8e00066a36')
        pass

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
