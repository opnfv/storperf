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

from unittest import mock

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
            """{"timestamp" : "975542400", "key":123.0 }""")
        result = testconv.convert_json_to_flat(json_object, "host.run-name")

        emitter = CarbonMetricTransmitter()
        emitter.carbon_port = self.listen_port
        emitter.transmit_metrics(result, None)

        self.assertEqual("host.run-name.key 123.0 975542400\n",
                         data[1].decode('utf-8'),
                         data)

    @mock.patch("socket.socket")
    @mock.patch("time.gmtime")
    def test_skip_non_numeric_metrics(self, mock_time, mock_socket):

        mock_socket.side_effect = MockSocket

        mock_time.return_value = strptime("30 Nov 00", "%d %b %y")

        testconv = converter.Converter()
        json_object = json.loads(
            """{"timestamp" : "975542400", "key":"value" }""")
        result = testconv.convert_json_to_flat(json_object, "host.run-name")

        emitter = CarbonMetricTransmitter()
        emitter.carbon_port = self.listen_port
        emitter.transmit_metrics(result, None)

        self.assertEqual("None.commit-marker 975542400 975542400\n",
                         data[1].decode('utf-8'),
                         data[1])

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
        emitter.transmit_metrics(result, None)

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
        emitter.transmit_metrics(result, None)

        self.assertEqual(0,
                         len(data),
                         len(data))

    @mock.patch("storperf.db.graphite_db.GraphiteDB.fetch_item")
    def test_confirm_commit(self, mock_graphite_db):
        graphite_return = json.loads("""[
          {"target":
           "rw.queue-depth.2.block-size.2048.10-10-243-154.commit-marker",
           "datapoints": [[1503078366.0, 1503078370]]}]
           """)
        mock_graphite_db.return_value = graphite_return

        commit_marker = "commit-marker"

        emitter = CarbonMetricTransmitter()
        emitter.commit_markers[commit_marker] = 1503078366

        committed = emitter.confirm_commit(commit_marker)
        self.assertTrue(committed)

    @mock.patch("storperf.db.graphite_db.GraphiteDB.fetch_item")
    def test_confirm_multiple_commits(self, mock_graphite_db):
        graphite_return = json.loads("""[
          {"target":
           "rw.queue-depth.2.block-size.2048.10-10-243-154.commit-marker",
           "datapoints": [
             [1503078300.0, 1503078350],
             [1503078366.0, 1503078360]]}]
           """)
        mock_graphite_db.return_value = graphite_return

        commit_marker = "commit-marker"

        emitter = CarbonMetricTransmitter()
        emitter.commit_markers[commit_marker] = 1503078366

        committed = emitter.confirm_commit(commit_marker)
        self.assertTrue(committed)

    @mock.patch("storperf.db.graphite_db.GraphiteDB.fetch_item")
    def test_empty_commit(self, mock_graphite_db):
        graphite_return = json.loads("[]")
        mock_graphite_db.return_value = graphite_return

        commit_marker = "commit-marker"

        emitter = CarbonMetricTransmitter()
        emitter.commit_markers[commit_marker] = 1503078366

        committed = emitter.confirm_commit(commit_marker)
        self.assertFalse(committed)

    @mock.patch("storperf.db.graphite_db.GraphiteDB.fetch_item")
    def test_badtimestamp_commit(self, mock_graphite_db):
        graphite_return = json.loads("""[
          {"target":
           "rw.queue-depth.2.block-size.2048.10-10-243-154.commit-marker",
           "datapoints": [[1234, 1503078370]]}]
           """)
        mock_graphite_db.return_value = graphite_return

        commit_marker = "commit-marker"

        emitter = CarbonMetricTransmitter()
        emitter.commit_markers[commit_marker] = 1503078366

        committed = emitter.confirm_commit(commit_marker)
        self.assertFalse(committed)

    def test_timestamp_parse(self):
        emitter = CarbonMetricTransmitter()
        result = json.loads("""[
          {"target":
           "rw.queue-depth.2.block-size.2048.10-10-243-154.commit-marker",
           "datapoints": [[1503078366.0, 1503078370]]}]
           """)
        timestamps = emitter.parse_timestamp(result)
        self.assertEqual(1503078366, timestamps[0], timestamps[0])


if __name__ == '__main__':
    unittest.main()
