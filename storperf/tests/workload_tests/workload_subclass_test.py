##############################################################################
# Copyright (c) 2015 EMC and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import unittest
from storperf.workloads.rr import rr
from storperf.workloads.rs import rs
from storperf.workloads.rw import rw
from storperf.workloads.wr import wr
from storperf.workloads.ws import ws


class WorkloadSubclassTest(unittest.TestCase):

    def setUp(self):
        pass

    def test_local_name(self):
        workload = rr()
        self.assertEqual(workload.fullname,
                         "None.rr.None.queue-depth.1.block-size.64k",
                         workload.fullname)

    def test_remote_name(self):
        workload = rw()
        workload.remote_host = "192.168.0.1"
        self.assertEqual(workload.fullname,
                         "None.rw.192-168-0-1.queue-depth.1.block-size.64k",
                         workload.fullname)

    def test_blocksize(self):
        workload = rs()
        workload.options["bs"] = "4k"
        self.assertEqual(workload.fullname,
                         "None.rs.None.queue-depth.1.block-size.4k",
                         workload.fullname)

    def test_queue_depth(self):
        workload = wr()
        workload.options["iodepth"] = "8"
        self.assertEqual(workload.fullname,
                         "None.wr.None.queue-depth.8.block-size.64k",
                         workload.fullname)

    def test_id(self):
        workload = ws()
        workload.id = "workloadid"
        self.assertEqual(workload.fullname,
                         "workloadid.ws.None.queue-depth.1.block-size.64k",
                         workload.fullname)
