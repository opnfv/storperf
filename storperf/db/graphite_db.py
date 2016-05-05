from storperf.db.job_db import JobDB
import json
import logging

import requests


class GraphiteDB(object):

    def __init__(self):
        """
        """
        self._job_db = JobDB()
        self.logger = logging.getLogger(__name__)

    def fetch_averages(self, workload):
        workload_executions = self._job_db.fetch_workloads(workload)

        # Create a map of job runs
        workload_names = {}
        for workload_execution in workload_executions:
            name = '.'.join(workload_execution[0].split('.')[0:6])
            if name in workload_names:
                workload_record = workload_names[name]
                start = workload_record[0]
                end = workload_record[1]
            else:
                start = None
                end = None

            if start is None or workload_execution[1] < start:
                start = workload_execution[1]

            if end is None or workload_execution[2] > end:
                end = workload_execution[2]

            workload_names[name] = [start, end]

        averages = {}

        for io_type in ['read', 'write']:
            for workload_name, times in workload_names.iteritems():
                workload_pattern = self.make_fullname_pattern(workload_name)
                request = ("http://127.0.0.1:8000/render/?target="
                           "averageSeries(%s.jobs.1.%s.lat.mean)"
                           "&format=json"
                           "&from=%s"
                           "&until=%s" %
                           (workload_pattern, io_type, times[0], times[1]))
                self.logger.debug("Calling %s" % (request))

                response = requests.get(request)
                if (response.status_code == 200):
                    averages[workload_name] = self._average_results(
                        json.loads(response.content))

        return averages

    def _average_results(self, results):

        for item in results:
            datapoints = item['datapoints']

            total = 0
            count = 0

            for datapoint in datapoints:
                if datapoint[0] is not None:
                    total += datapoint[0]
                    count += 1

            average = total / count

        return average

    def make_fullname_pattern(self, workload):
        parts = workload.split('.')
        wildcards_needed = 7 - len(parts)
        fullname = workload + (".*" * wildcards_needed)
        return fullname
