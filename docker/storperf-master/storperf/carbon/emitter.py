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

    carbon_servers = [('127.0.0.1', 2003),
                      ('storperf-graphite', 2003)]

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def transmit_metrics(self, metrics):
        if 'timestamp' in metrics:
            metrics.pop('timestamp')
        timestamp = str(calendar.timegm(time.gmtime()))
        carbon_socket = None

        for host, port in self.carbon_servers:
            try:
                carbon_socket = socket.socket(socket.AF_INET,
                                              socket.SOCK_STREAM)
                carbon_socket.connect((host, port))

                for key, metric in metrics.items():
                    message = key + " " + metric + " " + timestamp
                    self.logger.debug("Metric: " + message)
                    carbon_socket.send(message + '\n')

                self.logger.info("Sent metrics to %s:%s with timestamp %s"
                                 % (host, port, timestamp))

            except Exception, e:
                self.logger.error("While notifying carbon %s:%s %s"
                                  % (host, port, e))

            if carbon_socket is not None:
                carbon_socket.close()
