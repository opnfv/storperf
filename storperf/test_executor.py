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
import os
import socket

from os import listdir
from os.path import isfile, join

from fio.fio_invoker import FIOInvoker
from carbon.emitter import CarbonMetricTransmitter
from carbon.converter import JSONToCarbon


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
        self.prefix = socket.getfqdn()
        self.job_id = None

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

        if (workloads is None or workloads.length() == 0):
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

    def create_job_id(self):
        return 1234

    def execute(self):
        if (self.job_id is None):
            self.job_id = self.create_job_id()

        invoker = FIOInvoker()
        invoker.register(self.event)

        for numjobs in [1, 2, 4]:

            for workload_module in self.workload_modules:
                constructor = getattr(workload_module, "__name__")
                constructorMethod = getattr(workload_module, constructor)
                self.logger.debug(
                    "Found constructor: " + str(constructorMethod))
                workload = constructorMethod()
                workload.filename = self.filename
                workload.invoker = invoker
                workload.options['iodepth'] = str(numjobs)
                self.logger.info("Executing workload: " + constructor)
                workload.execute()
