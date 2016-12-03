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
from time import sleep
import time

from storperf.db import test_results_db
from storperf.db.graphite_db import GraphiteDB
from storperf.utilities import data_treatment as DataTreatment
from storperf.utilities import dictionary
from storperf.utilities import math as math
from storperf.utilities import steady_state as SteadyState


class DataHandler(object):

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.samples = 11

    """
    """

    def data_event(self, executor):
        self.logger.debug("Event received")

        if executor.terminated:
            self._push_to_db(executor)
        else:
            steady_state = True
            metrics = {}
            for metric in ('lat.mean', 'iops', 'bw'):
                metrics[metric] = {}
                for io_type in ('read', 'write'):
                    metrics[metric][io_type] = {}

                    series = self._lookup_prior_data(executor, metric, io_type)
                    steady = self._evaluate_prior_data(series)

                    self.logger.debug("Steady state for %s %s: %s"
                                      % (io_type, metric, steady))

                    metrics[metric][io_type]['series'] = series
                    metrics[metric][io_type]['steady_state'] = steady
                    treated_data = DataTreatment.data_treatment(series)

                    metrics[metric][io_type]['slope'] = \
                        math.slope(treated_data['slope_data'])
                    metrics[metric][io_type]['range'] = \
                        math.range_value(treated_data['range_data'])
                    metrics[metric][io_type]['average'] = \
                        math.average(treated_data['average_data'])

                    if not steady:
                        steady_state = False

            executor.metadata['report_data'] = metrics
            executor.metadata['steady_state'] = steady_state

            if steady_state:
                executor.terminate()

    def _lookup_prior_data(self, executor, metric, io_type):
        workload = executor.current_workload
        graphite_db = GraphiteDB()

        # A bit of a hack here as Carbon might not be finished storing the
        # data we just sent to it
        now = int(time.time())
        backtime = 60 * (self.samples + 2)
        data_series = graphite_db.fetch_series(workload,
                                               metric,
                                               io_type,
                                               now,
                                               backtime)
        most_recent_time = now
        if len(data_series) > 0:
            most_recent_time = data_series[-1][0]

        delta = now - most_recent_time
        self.logger.debug("Last update to graphite was %s ago" % delta)

        while (delta < 5 or (delta > 60 and delta < 120)):
            sleep(5)
            data_series = graphite_db.fetch_series(workload,
                                                   metric,
                                                   io_type,
                                                   now,
                                                   backtime)
            if len(data_series) > 0:
                most_recent_time = data_series[-1][0]
            delta = time.time() - most_recent_time
            self.logger.debug("Last update to graphite was %s ago" % delta)

        return data_series

    def _evaluate_prior_data(self, data_series):
        self.logger.debug("Data series: %s" % data_series)
        if len(data_series) == 0:
            return False
        earliest_timestamp = data_series[0][0]
        latest_timestamp = data_series[-1][0]
        duration = latest_timestamp - earliest_timestamp
        if (duration < 60 * self.samples):
            self.logger.debug("Only %s minutes of samples, ignoring" %
                              (duration / 60,))
            return False

        return SteadyState.steady_state(data_series)

    def _push_to_db(self, executor):
        test_db = os.environ.get('TEST_DB_URL')

        if test_db is not None:
            pod_name = dictionary.get_key_from_dict(executor.metadata,
                                                    'pod_name',
                                                    'Unknown')
            version = dictionary.get_key_from_dict(executor.metadata,
                                                   'version',
                                                   'Unknown')
            scenario = dictionary.get_key_from_dict(executor.metadata,
                                                    'scenario_name',
                                                    'Unknown')
            build_tag = dictionary.get_key_from_dict(executor.metadata,
                                                     'build_tag',
                                                     'Unknown')
            duration = executor.end_time - executor.start_time

            self.logger.info("Pushing results to %s" % (test_db))

            payload = executor.metadata
            payload['timestart'] = executor.start_time
            payload['duration'] = duration
            payload['status'] = 'OK'
            graphite_db = GraphiteDB()
            payload['metrics'] = graphite_db.fetch_averages(
                executor.job_db.job_id)
            criteria = {}
            criteria['block_sizes'] = executor.block_sizes
            criteria['queue_depths'] = executor.queue_depths

            try:
                test_results_db.push_results_to_db(test_db,
                                                   "storperf",
                                                   "Latency Test",
                                                   executor.start_time,
                                                   executor.end_time,
                                                   self.logger,
                                                   pod_name,
                                                   version,
                                                   scenario,
                                                   criteria,
                                                   build_tag,
                                                   payload)
            except:
                self.logger.exception("Error pushing results into Database")
