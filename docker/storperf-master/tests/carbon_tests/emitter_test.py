##############################################################################
# Copyright (c) 2015 EMC and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

import json
from time import strptime
import unittest

import mock

from storperf.carbon import converter
from storperf.carbon.emitter import CarbonMetricTransmitter


addresses = []
data = []
connect_exception = []
send_exception = []


class MockSocket(object):

    def __init__(self, *args):
        pass

    def connect(self, address):
        if len(connect_exception) != 0:
            raise connect_exception[0]
        addresses.append(address)

    def send(self, datum):
        if len(send_exception) != 0:
            raise send_exception[0]
        data.append(datum)

    def close(self):
        pass


class CarbonMetricTransmitterTest(unittest.TestCase):
    listen_port = 0
    response = None

    def setUp(self):
        del addresses[:]
        del data[:]
        del connect_exception[:]
        del send_exception[:]

    @mock.patch("socket.socket")
    @mock.patch("time.gmtime")
    def test_transmit_metrics(self, mock_time, mock_socket):

        mock_socket.side_effect = MockSocket

        mock_time.return_value = strptime("30 Nov 00", "%d %b %y")

        testconv = converter.Converter()
        json_object = json.loads(
            """{"timestamp" : "975542400", "key":"value" }""")
        result = testconv.convert_json_to_flat(json_object, "host.run-name")

        emitter = CarbonMetricTransmitter()
        emitter.carbon_port = self.listen_port
        emitter.transmit_metrics(result)

        self.assertEqual("host.run-name.key value 975542400\n",
                         data[0],
                         data[0])

    @mock.patch("socket.socket")
    def test_connect_fails(self, mock_socket):

        mock_socket.side_effect = MockSocket
        connect_exception.append(Exception("Mock connection error"))

        testconv = converter.Converter()
        json_object = json.loads(
            """{"timestamp" : "975542400", "key":"value" }""")
        result = testconv.convert_json_to_flat(json_object, "host.run-name")

        emitter = CarbonMetricTransmitter()
        emitter.carbon_port = self.listen_port
        emitter.transmit_metrics(result)

        self.assertEqual(0,
                         len(data),
                         len(data))

    @mock.patch("socket.socket")
    def test_send_fails(self, mock_socket):

        mock_socket.side_effect = MockSocket
        send_exception.append(Exception("Mock send error"))

        testconv = converter.Converter()
        json_object = json.loads(
            """{"timestamp" : "975542400", "key":"value" }""")
        result = testconv.convert_json_to_flat(json_object, "host.run-name")

        emitter = CarbonMetricTransmitter()
        emitter.carbon_port = self.listen_port
        emitter.transmit_metrics(result)

        self.assertEqual(0,
                         len(data),
                         len(data))


if __name__ == '__main__':
    unittest.main()
