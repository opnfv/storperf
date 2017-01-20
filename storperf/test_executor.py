##############################################################################
# Copyright (c) 2016 EMC and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

import copy
import imp
import logging
from os import listdir
import os
from os.path import isfile, join
import sched
from threading import Thread
import time

from storperf.carbon.converter import Converter
from storperf.carbon.emitter import CarbonMetricTransmitter
from storperf.db.job_db import JobDB
from storperf.fio.fio_invoker import FIOInvoker
from storperf.utilities.data_handler import DataHandler
from storperf.utilities.thread_gate import ThreadGate


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
        self.metadata = {}
        self.start_time = None
        self.end_time = None
        self.current_workload = None
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
        self._thread_gate = None

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

    @property
    def terminated(self):
        return self._terminated

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

        if self._thread_gate.report(callback_id):
            self.broadcast_event()

    def broadcast_event(self):
        for event_listener in self.event_listeners:
            try:
                self.logger.debug("Notifying event listener %s",
                                  event_listener)
                event_listener(self)
            except Exception, e:
                self.logger.exception("While notifying listener %s", e)

    def register_workloads(self, workloads):
        self.workload_modules = []

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
                                       args=(),
                                       name="Workload thread")
        self._workload_thread.start()
        return self.job_db.job_id

    def terminate(self):
        self._terminated = True
        self.end_time = time.time()
        return self._terminate_current_run()

    def _terminate_current_run(self):
        self.logger.info("Terminating current run")
        terminated_hosts = []
        for workload in self._workload_executors:
            workload.terminate()
            terminated_hosts.append(workload.remote_host)
        return terminated_hosts

    def execution_status(self, job_id):
        if self.job_db.job_id != job_id:
            return "Completed"

        if (self._terminated is False):
            return "Running"

        return "Completed"

    def execute_workloads(self):
        self._terminated = False
        self.logger.info("Starting job %s" % (self.job_db.job_id))
        self.event_listeners.clear()
        data_handler = DataHandler()
        self.register(data_handler.data_event)

        self.start_time = time.time()

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
            self._thread_gate = ThreadGate(len(self.slaves),
                                           workload.options['status-interval'])

            for blocksize in blocksizes:
                for iodepth in iodepths:

                    if self._terminated:
                        return
                    self.current_workload = (
                        "%s.%s.queue-depth.%s.block-size.%s" %
                        (self.job_db.job_id,
                         workload_name,
                         iodepth,
                         blocksize))

                    self.logger.info("Starting run %s" % self.current_workload)

                    scheduler = sched.scheduler(time.time, time.sleep)
                    if self.deadline is not None \
                            and not workload_name.startswith("_"):
                        event = scheduler.enter(self.deadline * 60, 1,
                                                self._terminate_current_run,
                                                ())
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
                                   args=(slave_workload,),
                                   name="%s worker" % slave)
                        t.daemon = False
                        t.start()
                        slave_threads.append(t)

                    for slave_thread in slave_threads:
                        self.logger.debug("Waiting on %s" % slave_thread)
                        slave_thread.join()
                        self.logger.debug("Done waiting for %s" % slave_thread)

                    if not scheduler.empty():
                        try:
                            scheduler.cancel(event)
                        except:
                            pass

                    self.logger.info("Completed run %s" %
                                     self.current_workload)
                    self._workload_executors = []
                    self.current_workload = None

            self.logger.info("Completed workload %s" % (workload_name))
        self.logger.info("Completed job %s" % (self.job_db.job_id))

        self.end_time = time.time()
        self._terminated = True
        self.broadcast_event()
        self.unregister(data_handler.data_event)

    def execute_on_node(self, workload):

        invoker = FIOInvoker()
        invoker.register(self.event)
        workload.invoker = invoker

        self.logger.info("Starting " + workload.fullname)

        self.job_db.start_workload(workload)
        workload.execute()
        self.job_db.end_workload(workload)
        invoker.unregister(self.event)

        self.logger.info("Ended " + workload.fullname)
