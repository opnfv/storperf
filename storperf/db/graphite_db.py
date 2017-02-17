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

from storperf.db.job_db import JobDB


class GraphiteDB(object):

    def __init__(self):
        """
        """
        self._job_db = JobDB()
        self.logger = logging.getLogger(__name__)

    def fetch_series(self, workload, metric, io_type, time, duration):

        series = []
        end = time
        start = end - duration

        request = ("http://127.0.0.1:8000/render/?target="
                   "averageSeries(%s.*.jobs.1.%s.%s)"
                   "&format=json"
                   "&from=%s"
                   "&until=%s" %
                   (workload, io_type, metric,
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
