##############################################################################
# Copyright (c) 2015 EMC and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import calendar
import logging
import socket
import time


class CarbonMetricTransmitter():

    carbon_host = '127.0.0.1'
    carbon_port = 2003

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def transmit_metrics(self, metrics):
        if 'timestamp' in metrics:
            timestamp = metrics.pop('timestamp')
        else:
            timestamp = str(calendar.timegm(time.gmtime()))

        self.carbon_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.carbon_socket.connect((self.carbon_host, self.carbon_port))

        for key, metric in metrics.items():
            message = key + " " + metric + " " + timestamp
            self.logger.debug("Metric: " + message)
            self.carbon_socket.send(message + '\n')

        self.carbon_socket.close()
