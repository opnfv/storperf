##############################################################################
# Copyright (c) 2015 EMC and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

import imp
import logging
from os import listdir
import os
from os.path import isfile, join
import socket

from carbon.converter import JSONToCarbon
from carbon.emitter import CarbonMetricTransmitter
from db.job_db import JobDB
from fio.fio_invoker import FIOInvoker


class UnknownWorkload(Exception):

    def __init__(self, msg):
        self.msg = msg


class TestExecutor(object):

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.workload_modules = []
        self.filename = "storperf.dat"
        self.precondition = True
        self.warm = True
        self.event_listeners = set()
        self.metrics_converter = JSONToCarbon()
        self.metrics_emitter = CarbonMetricTransmitter()
        self.prefix = None
        self.job_db = JobDB()

    def register(self, event_listener):
        self.event_listeners.add(event_listener)

    def unregister(self, event_listener):
        self.event_listeners.discard(event_listener)

    def event(self, metric):
        carbon_metrics = self.metrics_converter.convert_to_dictionary(
            metric,
            self.prefix)

        read_latency = carbon_metrics[self.prefix + ".jobs.1.read.lat.mean"]
        write_latency = carbon_metrics[self.prefix + ".jobs.1.write.lat.mean"]
        read_iops = carbon_metrics[self.prefix + ".jobs.1.read.iops"]
        write_iops = carbon_metrics[self.prefix + ".jobs.1.write.iops"]

        message = "Average Latency us Read/Write: " + read_latency \
            + "/" + write_latency + " IOPS r/w: " + \
            read_iops + "/" + write_iops

        for event_listener in self.event_listeners:
            event_listener(message)

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
                mname, ext = os.path.splitext(filename)
                if (not mname.startswith('_')):
                    workloads.append(mname)

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
                    raise UnknownWorkload("Unknown workload: " + workload)
                self.workload_modules.append(workload_module)
            except ImportError, err:
                raise UnknownWorkload(err)

    def load_from_file(self, uri):
        uri = os.path.normpath(os.path.join(os.path.dirname(__file__), uri))
        path, fname = os.path.split(uri)
        mname, ext = os.path.splitext(fname)
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

        shortname = socket.getfqdn().split('.')[0]

        invoker = FIOInvoker()
        invoker.register(self.event)
        self.job_db.create_job_id()
        self.logger.info("Starting job " + self.job_db.job_id)

        for workload_module in self.workload_modules:

            workload_name = getattr(workload_module, "__name__")
            constructorMethod = getattr(workload_module, workload_name)
            self.logger.debug(
                "Found workload: " + str(constructorMethod))
            workload = constructorMethod()
            workload.filename = self.filename
            workload.invoker = invoker

            if (workload_name.startswith("_")):
                iodepths = [2, ]
                blocksizes = [4096, ]
            else:
                iodepths = [1, 16, 128]
                blocksizes = [4096, 65536, 1048576]

            for blocksize in blocksizes:
                for iodepth in iodepths:

                    full_workload_name = workload_name + \
                        ".queue-depth." + str(iodepth) + \
                        ".block-size." + str(blocksize)

                    workload.options['iodepth'] = str(iodepth)
                    workload.options['bs'] = str(blocksize)
                    self.logger.info(
                        "Executing workload: " + full_workload_name)

                    self.prefix = shortname + "." + self.job_db.job_id + \
                        "." + full_workload_name

                    self.job_db.start_workload(full_workload_name)
                    workload.execute()
                    self.job_db.end_workload(full_workload_name)

        self.logger.info("Finished job " + self.job_db.job_id)

    def fetch_results(self, job, workload_name=""):
        self.job_db.job_id = job
        return self.job_db.fetch_results(workload_name)
