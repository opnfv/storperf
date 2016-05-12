##############################################################################
# Copyright (c) 2016 EMC and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

from os import listdir
from os.path import isfile, join
from storperf.carbon.converter import Converter
from storperf.carbon.emitter import CarbonMetricTransmitter
from storperf.db import test_results_db
from storperf.db.graphite_db import GraphiteDB
from storperf.db.job_db import JobDB
from storperf.fio.fio_invoker import FIOInvoker
from storperf.utilities import dictionary
from threading import Thread
import copy
import imp
import logging
import os
import sched
import time


class UnknownWorkload(Exception):
    pass


class TestExecutor(object):

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.workload_modules = []
        self.filename = None
        self.precondition = True
        self.deadline = None
        self.warm = True
        self.metadata = None
        self._queue_depths = [1, 4, 8]
        self._block_sizes = [512, 4096, 16384]
        self.event_listeners = set()
        self.metrics_converter = Converter()
        self.metrics_emitter = CarbonMetricTransmitter()
        self.prefix = None
        self.job_db = JobDB()
        self._slaves = []
        self._terminated = False
        self._workload_executors = []
        self._workload_thread = None

    @property
    def slaves(self):
        return self._slaves

    @slaves.setter
    def slaves(self, slaves):
        self.logger.debug("Set slaves to: " + str(slaves))
        self._slaves = slaves

    @property
    def queue_depths(self):
        return ','.join(self._queue_depths)

    @queue_depths.setter
    def queue_depths(self, queue_depths):
        self.logger.debug("Set queue_depths to: " + str(queue_depths))
        self._queue_depths = queue_depths.split(',')

    @property
    def block_sizes(self):
        return ','.join(self._block_sizes)

    @block_sizes.setter
    def block_sizes(self, block_sizes):
        self.logger.debug("Set block_sizes to: " + str(block_sizes))
        self._block_sizes = block_sizes.split(',')

    def register(self, event_listener):
        self.event_listeners.add(event_listener)

    def unregister(self, event_listener):
        self.event_listeners.discard(event_listener)

    def event(self, callback_id, metric):
        carbon_metrics = self.metrics_converter.convert_json_to_flat(
            metric,
            callback_id)

        self.metrics_emitter.transmit_metrics(carbon_metrics)

    def register_workloads(self, workloads):
        if (workloads is None or len(workloads) == 0):
            workload_dir = os.path.normpath(
                os.path.join(os.path.dirname(__file__), "workloads"))

            workload_files = [
                f for f in listdir(workload_dir)
                if isfile(join(workload_dir, f))]

            workloads = []

            for filename in workload_files:
                mname, _ = os.path.splitext(filename)
                if (not mname.startswith('_')):
                    workloads.append(mname)
        else:
            workloads = workloads.split(',')

        if (self.warm is True):
            workloads.insert(0, "_warm_up")

        if (self.precondition is True):
            workloads.insert(0, "_ssd_preconditioning")

        for workload in workloads:
            try:
                workload_module = self.load_from_file("workloads/" +
                                                      workload + ".py")
                self.logger.debug("Found: " + str(workload_module))
                if(workload_module is None):
                    raise UnknownWorkload(
                        "ERROR: Unknown workload: " + workload)
                if workload_module not in self.workload_modules:
                    self.workload_modules.append(workload_module)
            except ImportError, err:
                raise UnknownWorkload("ERROR: " + str(err))

    def load_from_file(self, uri):
        uri = os.path.normpath(os.path.join(os.path.dirname(__file__), uri))
        path, fname = os.path.split(uri)
        mname, _ = os.path.splitext(fname)
        no_ext = os.path.join(path, mname)
        self.logger.debug("Looking for: " + no_ext)
        if os.path.exists(no_ext + '.pyc'):
            self.logger.debug("Loading compiled: " + mname + " from " + no_ext)
            return imp.load_compiled(mname, no_ext + '.pyc')
        if os.path.exists(no_ext + '.py'):
            self.logger.debug("Compiling: " + mname + " from " + no_ext)
            return imp.load_source(mname, no_ext + '.py')
        return None

    def execute(self, metadata):
        self.job_db.create_job_id()
        self.job_db.record_workload_params(metadata)
        self.metadata = metadata
        self._workload_thread = Thread(target=self.execute_workloads,
                                       args=())
        self._workload_thread.start()
        return self.job_db.job_id

    def terminate(self):
        self._terminated = True
        return self.terminate_current_run()

    def terminate_current_run(self):
        self.logger.info("Terminating current run")
        terminated_hosts = []
        for workload in self._workload_executors:
            workload.terminate()
            terminated_hosts.append(workload.remote_host)
        return terminated_hosts

    def execute_workloads(self):
        self._terminated = False
        self.logger.info("Starting job %s" % (self.job_db.job_id))

        start_time = time.time()

        for workload_module in self.workload_modules:
            workload_name = getattr(workload_module, "__name__")
            self.logger.info("Starting workload %s" % (workload_name))

            constructorMethod = getattr(workload_module, workload_name)
            workload = constructorMethod()
            if (self.filename is not None):
                workload.filename = self.filename

            if (workload_name.startswith("_")):
                iodepths = [8, ]
                blocksizes = [16384, ]
            else:
                iodepths = self._queue_depths
                blocksizes = self._block_sizes

            workload.id = self.job_db.job_id

            for blocksize in blocksizes:
                for iodepth in iodepths:

                    scheduler = sched.scheduler(time.time, time.sleep)
                    if self._terminated:
                        return

                    if self.deadline is not None \
                            and not workload_name.startswith("_"):
                        event = scheduler.enter(self.deadline * 60, 1,
                                                self.terminate_current_run, ())
                        t = Thread(target=scheduler.run, args=())
                        t.start()

                    workload.options['iodepth'] = str(iodepth)
                    workload.options['bs'] = str(blocksize)

                    slave_threads = []
                    for slave in self.slaves:
                        slave_workload = copy.copy(workload)
                        slave_workload.remote_host = slave

                        self._workload_executors.append(slave_workload)

                        t = Thread(target=self.execute_on_node,
                                   args=(slave_workload,))
                        t.daemon = False
                        t.start()
                        slave_threads.append(t)

                    for slave_thread in slave_threads:
                        slave_thread.join()

                    if not scheduler.empty():
                        try:
                            scheduler.cancel(event)
                        except:
                            pass

                    self._workload_executors = []

            self.logger.info("Completed workload %s" % (workload_name))
        self.logger.info("Completed job %s" % (self.job_db.job_id))
        end_time = time.time()
        pod_name = dictionary.get_key_from_dict(self.metadata,
                                                'pod_name',
                                                'Unknown')
        version = dictionary.get_key_from_dict(self.metadata,
                                               'version',
                                               'Unknown')
        scenario = dictionary.get_key_from_dict(self.metadata,
                                                'scenario',
                                                'Unknown')
        build_tag = dictionary.get_key_from_dict(self.metadata,
                                                 'build_tag',
                                                 'Unknown')
        duration = end_time - start_time
        test_db = os.environ.get('TEST_DB_URL')

        if test_db is not None:
            # I really do not like doing this.  As our threads just
            # terminated, their final results are still being spooled
            # off to Carbon.  Need to give that a little time to finish
            time.sleep(5)
            self.logger.info("Pushing results to %s" % (test_db))

            payload = self.metadata
            payload['timestart'] = start_time
            payload['duration'] = duration
            payload['status'] = 'OK'
            graphite_db = GraphiteDB()
            payload['metrics'] = graphite_db.fetch_averages(self.job_db.job_id)
            criteria = {}
            criteria['block_sizes'] = self.block_sizes
            criteria['queue_depths'] = self.block_sizes

            try:
                test_results_db.push_results_to_db(test_db,
                                                   "storperf",
                                                   "Latency Test",
                                                   self.logger,
                                                   pod_name,
                                                   version,
                                                   scenario,
                                                   criteria,
                                                   build_tag,
                                                   payload)
            except:
                self.logger.exception("Error pushing results into Database")

    def execute_on_node(self, workload):

        invoker = FIOInvoker()
        invoker.register(self.event)
        workload.invoker = invoker

        self.logger.info("Starting " + workload.fullname)

        self.job_db.start_workload(workload)
        workload.execute()
        self.job_db.end_workload(workload)

        self.logger.info("Ended " + workload.fullname)
