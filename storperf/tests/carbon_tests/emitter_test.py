##############################################################################
# Copyright (c) 2015 EMC and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

from storperf.carbon import converter
from storperf.carbon.emitter import CarbonMetricTransmitter
from time import sleep
import SocketServer
import json
import threading
import unittest


class MetricsHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        # Echo the back to the client
        CarbonMetricTransmitterTest.response = self.request.recv(1024)
        return


class MetricsServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass


class CarbonMetricTransmitterTest(unittest.TestCase):
    listen_port = 0
    response = None

    def setUp(self):

        address = ('localhost', 0)
        server = MetricsServer(address, MetricsHandler)
        ip, self.listen_port = server.server_address

        t = threading.Thread(target=server.serve_forever)
        t.setDaemon(True)
        t.start()

    def test_transmit_metrics(self):

        testconv = converter.Converter()
        json_object = json.loads("""{"timestamp" : "12345", "key":"value" }""")
        result = testconv.convert_json_to_flat(json_object, "host.run-name")

        emitter = CarbonMetricTransmitter()
        emitter.carbon_port = self.listen_port
        emitter.transmit_metrics(result)

        count = 0

        while (CarbonMetricTransmitterTest.response is None and count < 10):
            count += 1
            sleep(0.1)

        self.assertEqual("host.run-name.key value 12345\n",
                         CarbonMetricTransmitterTest.response,
                         CarbonMetricTransmitterTest.response)

if __name__ == '__main__':
    unittest.main()
