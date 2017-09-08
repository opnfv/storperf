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

from storperf.db.graphite_db import GraphiteDB


class CarbonMetricTransmitter():

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.graphite_db = GraphiteDB()
        self.commit_markers = {}
        self.host = 'storperf-graphite'
        self.port = 2003

    def transmit_metrics(self, metrics, commit_marker):
        timestamp = str(calendar.timegm(time.gmtime()))
        self.commit_markers[commit_marker] = int(timestamp)

        carbon_socket = None

        try:
            carbon_socket = socket.socket(socket.AF_INET,
                                          socket.SOCK_STREAM)
            carbon_socket.connect((self.host, self.port))

            for key, value in metrics.items():
                try:
                    float(value)
                    message = "%s %s %s\n" \
                        % (key, value, timestamp)
                    self.logger.debug("Metric: " + message.strip())
                    carbon_socket.send(message)
                except ValueError:
                    self.logger.debug("Ignoring non numeric metric %s %s"
                                      % (key, value))

            message = "%s.commit-marker %s %s\n" \
                % (commit_marker, timestamp, timestamp)
            carbon_socket.send(message)
            self.logger.debug("Marker %s" % message.strip())
            self.logger.info("Sent metrics to %s:%s with timestamp %s"
                             % (self.host, self.port, timestamp))

        except Exception, e:
            self.logger.error("While notifying carbon %s:%s %s"
                              % (self.host, self.port, e))

        if carbon_socket is not None:
            carbon_socket.close()

    def confirm_commit(self, commit_marker):
        marker_timestamp = self.commit_markers[commit_marker]
        request = "%s.commit-marker&from=%s" \
            % (commit_marker, marker_timestamp - 60)
        marker_data = self.graphite_db.fetch_item(request)
        self.logger.debug("Marker data %s" % marker_data)
        fetched_timestamps = self.parse_timestamp(marker_data)

        return marker_timestamp in fetched_timestamps

    def parse_timestamp(self, marker_data):
        timestamps = []
        if (type(marker_data) is list and
                len(marker_data) > 0):
            datapoints = marker_data[0]['datapoints']
            for datapoint in datapoints:
                try:
                    timestamps.append(int(datapoint[0]))
                except Exception:
                    pass

        return timestamps
