##############################################################################
# Copyright (c) 2016 EMC and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

import json
import logging
import requests


class GraphiteDB(object):

    graphite_host = "storperf-graphite"
    graphite_port = 8080

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def fetch_item(self, target):

        result = None
        request = ("http://%s:%s/graphite/render/?format=json&target=%s"
                   % (self.graphite_host, self.graphite_port, target))
        self.logger.debug("Calling %s" % (request))

        response = requests.get(request)
        if (response.status_code == 200):
            result = json.loads(response.content)

        return result

    def fetch_series(self, workload, metric, io_type, time, duration):

        series = []
        end = time
        start = end - duration

        request = ("http://%s:%s/graphite/render/?target="
                   "averageSeries(%s.*.jobs.1.%s.%s)"
                   "&format=json"
                   "&from=%s"
                   "&until=%s"
                   % (self.graphite_host, self.graphite_port,
                      workload, io_type, metric,
                      start, end))
        self.logger.debug("Calling %s" % (request))

        response = requests.get(request)
        if (response.status_code == 200):
            series = self._series_results(json.loads(response.content))

        return series

    def _series_results(self, results):

        series = []

        for item in results:
            datapoints = item['datapoints']
            for datapoint in datapoints:
                if datapoint[0] is not None:
                    series.append([datapoint[1], datapoint[0]])

        return series

    def make_fullname_pattern(self, workload):
        parts = workload.split('.')
        wildcards_needed = 7 - len(parts)
        fullname = workload + (".*" * wildcards_needed)
        return fullname
