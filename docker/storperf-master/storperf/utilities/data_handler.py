##############################################################################
# Copyright (c) 2016 Dell EMC and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

import logging
import os
import time

from storperf.db import test_results_db
from storperf.db.graphite_db import GraphiteDB
from storperf.db.job_db import JobDB
from storperf.utilities import data_treatment as DataTreatment
from storperf.utilities import math as math
from storperf.utilities import steady_state as SteadyState


class DataHandler(object):

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.job_db = JobDB()

    """
    """

    def data_event(self, executor):
        self.logger.debug("Event received")

        if executor.terminated:
            self._push_to_db(executor)
        else:
            workload = '.'.join(executor.current_workload.split('.')[1:6])

            steady_state = True
            metrics = {}
            for metric in ('lat_ns.mean', 'iops', 'bw'):
                metrics[metric] = {}
                for io_type in ('read', 'write'):
                    metrics[metric][io_type] = {}

                    function = "sumSeries"
                    if 'mean' in metric:
                        function = "averageSeries"

                    series = self._lookup_prior_data(executor, metric, io_type,
                                                     function)
                    series = self._convert_timestamps_to_samples(
                        executor, series)
                    steady = self._evaluate_prior_data(
                        series, executor.steady_state_samples)

                    self.logger.debug("Steady state for %s %s: %s"
                                      % (io_type, metric, steady))

                    metrics[metric][io_type]['series'] = series
                    metrics[metric][io_type]['steady_state'] = steady
                    treated_data = DataTreatment.data_treatment(series)

                    metrics[metric][io_type]['slope'] = \
                        math.slope(treated_data['slope_data'])
                    metrics[metric][io_type]['range'] = \
                        math.range_value(treated_data['range_data'])
                    average = math.average(treated_data['average_data'])
                    metrics[metric][io_type]['average'] = average

                    metrics_key = '%s.%s.%s' % (workload, io_type, metric)
                    executor.metadata['details']['metrics'][metrics_key] = \
                        average

                    if not steady:
                        steady_state = False

            if 'report_data' not in executor.metadata['details']:
                executor.metadata['details']['report_data'] = {}

            if 'steady_state' not in executor.metadata['details']:
                executor.metadata['details']['steady_state'] = {}

            executor.metadata['details']['report_data'][workload] = metrics
            executor.metadata['details']['steady_state'][workload] = \
                steady_state

            workload_name = executor.current_workload.split('.')[1]

            if steady_state and not workload_name.startswith('_'):
                executor.terminate_current_run()

    def _lookup_prior_data(self, executor, metric, io_type, function):
        workload = executor.current_workload
        graphite_db = GraphiteDB()

        # A bit of a hack here as Carbon might not be finished storing the
        # data we just sent to it
        now = int(time.time())
        backtime = 60 * (executor.steady_state_samples + 1)
        data_series = graphite_db.fetch_series(function,
                                               workload,
                                               metric,
                                               io_type,
                                               now,
                                               backtime)
        return data_series

    def _convert_timestamps_to_samples(self, executor, series):
        workload_record = self.job_db.fetch_workloads(
            executor.current_workload)
        start_time = int(workload_record[0][1])

        normalized_series = []

        for item in series:
            elapsed = (item[0] - start_time)
            sample_number = int(round(float(elapsed) / 60))
            normalized_series.append([sample_number, item[1]])

        return normalized_series

    def _evaluate_prior_data(self, data_series, samples):
        self.logger.debug("Data series: %s" % data_series)
        number_of_samples = len(data_series)

        if number_of_samples == 0:
            return False
        if (number_of_samples < samples):
            self.logger.debug("Only %s samples, ignoring" % number_of_samples)
            return False

        return SteadyState.steady_state(data_series)

    def _push_to_db(self, executor):
        executor.metadata['duration'] = executor.end_time - executor.start_time

        executor.metadata['timestart'] = executor.start_time

        criteria = self._determine_criteria(executor.metadata)
        executor.metadata['criteria'] = criteria

        executor.metadata['start_date'] = \
            time.strftime('%Y-%m-%d %H:%M:%S',
                          time.gmtime(executor.start_time))

        executor.metadata['stop_date'] = \
            time.strftime('%Y-%m-%d %H:%M:%S',
                          time.gmtime(executor.end_time))

        test_db = os.environ.get('TEST_DB_URL')
        if test_db is not None:
            self.logger.info("Pushing results to %s" % (test_db))
            try:
                response = test_results_db.push_results_to_db(
                    test_db,
                    executor.metadata,
                    self.logger)
                executor.result_url = response['href']
            except Exception:
                self.logger.exception("Error pushing results into Database")

    def _determine_criteria(self, metadata):
        steady_state = True
        for workload, value in metadata['details']['steady_state'].items():
            if not workload.startswith("_"):
                steady_state = steady_state and value

        if steady_state:
            return "PASS"
        else:
            return "FAIL"
