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

from storperf.db import test_results_db
from storperf.db.graphite_db import GraphiteDB
from storperf.utilities import dictionary


class DataHandler(object):

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    """
    """

    def data_event(self, executor):
        self.logger.info("Event received")

        # Data lookup

        if executor.terminated:
            self._push_to_db(executor)

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
