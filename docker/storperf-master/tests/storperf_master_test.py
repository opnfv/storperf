##############################################################################
# Copyright (c) 2015 EMC and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

import os
import unittest

from storperf.db.configuration_db import ConfigurationDB
from storperf.storperf_master import StorPerfMaster


class StorPerfMasterTest(unittest.TestCase):

    def setUp(self):
        ConfigurationDB.db_name = __name__ + '.db'
        try:
            os.remove(ConfigurationDB.db_name)
        except OSError:
            pass
        self.storperf = StorPerfMaster()

    def tearDown(self):
        try:
            os.remove(ConfigurationDB.db_name)
        except OSError:
            pass

    def test_agent_count(self):
        expected = 10

        self.storperf.agent_count = expected
        actual = self.storperf.agent_count

        self.assertEqual(
            expected, actual, "Did not expect: " + str(actual))

    def test_queue_depths(self):
        expected = "1,2,3"

        self.storperf.queue_depths = expected
        actual = self.storperf.queue_depths

        self.assertEqual(
            expected, actual, "Did not expect: " + str(actual))

    def test_block_sizes(self):
        expected = "8,2,1,0"

        self.storperf.block_sizes = expected
        actual = self.storperf.block_sizes

        self.assertEqual(
            expected, actual, "Did not expect: " + str(actual))

    def test_volume_size(self):
        expected = 20

        self.storperf.volume_size = expected
        actual = self.storperf.volume_size

        self.assertEqual(
            expected, actual, "Did not expect: " + str(actual))

    def test_agent_network(self):
        expected = "ABCDEF"

        self.storperf.public_network = expected
        actual = self.storperf.public_network

        self.assertEqual(
            expected, actual, "Did not expect: " + str(actual))

    def test_agent_flavor(self):
        expected = "m1.small"

        self.storperf.agent_flavor = expected
        actual = self.storperf.agent_flavor

        self.assertEqual(
            expected, actual, "Did not expect: " + str(actual))
