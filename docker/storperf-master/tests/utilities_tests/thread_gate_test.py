##############################################################################
# Copyright (c) 2016 EMC and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

import time
import unittest

from storperf.utilities.thread_gate import FailureToReportException
from storperf.utilities.thread_gate import ThreadGate


class ThreadGateTest(unittest.TestCase):

    def setUp(self):
        pass

    def test_one_one_report(self):
        gate = ThreadGate(1)
        self.assertEqual(True, gate.report(1))

    def test_two_one_report(self):
        gate = ThreadGate(2)
        self.assertEqual(False, gate.report(1))

    def test_two_two_reports(self):
        gate = ThreadGate(2)
        self.assertEqual(False, gate.report(1))
        self.assertEqual(True, gate.report(2))

    def test_two_one_duplicate_reports(self):
        gate = ThreadGate(2)
        self.assertEqual(False, gate.report(1))
        self.assertEqual(False, gate.report(1))
        self.assertEqual(True, gate.report(2))

    def test_two_old_old_report(self):
        timeout = 5
        gate = ThreadGate(2, timeout)
        report_time = time.time() - (timeout * 2)
        gate._registrants[2] = report_time
        self.assertEqual(False, gate.report(1))

    def test_two_never_report(self):
        timeout = 5
        gate = ThreadGate(2, timeout)
        report_time = time.time() - (timeout * 3)
        gate._creation_time = report_time
        try:
            gate.report(1)
            self.fail()
        except FailureToReportException:
            pass
