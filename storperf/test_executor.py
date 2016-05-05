##############################################################################
# Copyright (c) 2015 EMC and others.
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
from storperf.db.job_db import JobDB
from storperf.fio.fio_invoker import FIOInvoker
from threading import Thread
import copy
import imp
import logging
import os


class UnknownWorkload(Exception):
    pass


class TestExecutor(object):

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.workload_modules = []
        self.filename = None
        self.precondition = True
        self.warm = True
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

    def execute(self):
        self.job_db.create_job_id()
        self._workload_thread = Thread(target=self.execute_workloads, args=())
        self._workload_thread.start()
        return self.job_db.job_id

    def terminate(self):
        self._terminated = True
        for workload in self._workload_executors:
            workload.terminate()

    def execute_workloads(self):
        self._terminated = False
        for workload_module in self.workload_modules:
            workload_name = getattr(workload_module, "__name__")
            constructorMethod = getattr(workload_module, workload_name)
            workload = constructorMethod()
            if (self.filename is not None):
                workload.filename = self.filename

            if (workload_name.startswith("_")):
                iodepths = [32, ]
                blocksizes = [8192, ]
            else:
                iodepths = [128, 16, 1]
                blocksizes = [8192, 4096, 512]

            workload.id = self.job_db.job_id

            for blocksize in blocksizes:
                for iodepth in iodepths:
                    if self._terminated:
                        return

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

                    self._workload_executors = []

    def execute_on_node(self, workload):

        invoker = FIOInvoker()
        invoker.register(self.event)
        workload.invoker = invoker

        self.logger.info("Starting " + workload.fullname)

        self.job_db.start_workload(workload)
        workload.execute()
        self.job_db.end_workload(workload)

        self.logger.info("Ended " + workload.fullname)

    def fetch_workloads(self, job, workload_name=""):
        self.job_db.job_id = job
        return self.job_db.fetch_workloads(workload_name)
