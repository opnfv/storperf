##############################################################################
# Copyright (c) 2017 Dell EMC and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

import unittest

from storperf.utilities import ip_helper


class Test(unittest.TestCase):

    def testNoPortInIPv4(self):
        host, port = ip_helper.parse_address_and_port("127.0.0.1")
        self.assertEqual("127.0.0.1", host)
        self.assertEqual(22, port)

    def testPortInIPv4(self):
        host, port = ip_helper.parse_address_and_port("127.0.0.1:2222")
        self.assertEqual("127.0.0.1", host)
        self.assertEqual(2222, port)

    def testNoPortInIPv6(self):
        host, port = ip_helper.parse_address_and_port(
            "1fe80::58bb:c8b:f2f2:c888")
        self.assertEqual("1fe80::58bb:c8b:f2f2:c888",
                         host)
        self.assertEqual(22, port)

    def testPortInIPv6(self):
        host, port = ip_helper.parse_address_and_port(
            "[1fe80::58bb:c8b:f2f2:c888]:2222")
        self.assertEqual("1fe80::58bb:c8b:f2f2:c888",
                         host)
        self.assertEqual(2222, port)
