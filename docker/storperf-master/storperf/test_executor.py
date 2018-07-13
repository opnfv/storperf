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
import json
import logging
from multiprocessing.pool import ThreadPool
from os import listdir
import os
from os.path import isfile, join
import sched
from threading import Thread
from time import sleep
import time

from storperf.carbon.converter import Converter
from storperf.carbon.emitter import CarbonMetricTransmitter
from storperf.db.job_db import JobDB
from storperf.fio.fio_invoker import FIOInvoker
from storperf.utilities.data_handler import DataHandler
from storperf.utilities.thread_gate import ThreadGate
from storperf.workloads._custom_workload import _custom_workload


class UnknownWorkload(Exception):
    pass


class InvalidWorkloadName(Exception):
    pass


class TestExecutor(object):

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.workload_modules = []
        self._custom_workloads = {}
        self.filename = None
        self.deadline = None
        self.steady_state_samples = 10
        self.start_time = None
        self.end_time = None
        self.current_workload = None
        self.workload_status = {}
        self._queue_depths = [1, 4, 8]
        self._block_sizes = [512, 4096, 16384]
        self.event_listeners = set()
        self.metrics_converter = Converter()
        self.metrics_emitter = CarbonMetricTransmitter()
        self.prefix = None
        self.job_db = JobDB()
        self._slaves = []
        self._terminated = False
        self._volume_count = 1
        self._workload_executors = []
        self._workload_thread = None
        self._thread_gate = None
        self._setup_metadata({})

    def _setup_metadata(self, metadata={}):
        try:
            installer = os.environ['INSTALLER_TYPE']
        except KeyError:
            self.logger.warn("Cannot determine installer")
            installer = "Unknown_installer"

        self.metadata = {}
        self.metadata['project_name'] = 'storperf'
        self.metadata['installer'] = installer
        self.metadata['pod_name'] = 'Unknown'
        self.metadata['version'] = 'Unknown'
        self.metadata['scenario'] = 'Unknown'
        self.metadata['build_tag'] = 'Unknown'
        self.metadata['test_case'] = 'Unknown'
        self.metadata['details'] = {}
        self.metadata['details']['metrics'] = {}
        self.metadata.update(metadata)
        self.metadata['case_name'] = self.metadata['test_case']

    @property
    def slaves(self):
        return self._slaves

    @slaves.setter
    def slaves(self, slaves):
        self.logger.debug("Set slaves to: " + str(slaves))
        self._slaves = slaves

    @property
    def volume_count(self):
        return self._volume_count

    @volume_count.setter
    def volume_count(self, volume_count):
        self.logger.debug("Set volume count to: " + str(volume_count))
        self._volume_count = volume_count

    @property
    def custom_workloads(self):
        return self._custom_workloads

    @custom_workloads.setter
    def custom_workloads(self, custom_workloads):
        self.logger.debug("Set custom workloads to: %s " %
                          custom_workloads)
        self._custom_workloads = custom_workloads

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

    @property
    def job_id(self):
        return self.job_db.job_id

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

        self.metrics_emitter.transmit_metrics(carbon_metrics, callback_id)

        commit_count = 10
        while (commit_count > 0 and
               not self.metrics_emitter.confirm_commit(callback_id)):
            self.logger.info("Waiting 1 more second for commit")
            sleep(1)
            commit_count -= 1

        if self._thread_gate.report(callback_id):
            self.broadcast_event()

    def broadcast_event(self):
        for event_listener in self.event_listeners:
            try:
                self.logger.debug("Notifying event listener %s",
                                  event_listener)
                event_listener(self)
            except Exception as e:
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
            except ImportError as err:
                raise UnknownWorkload("ERROR: " + str(err))

    def load_from_file(self, uri):
        uri = os.path.normpath(os.path.join(os.path.dirname(__file__), uri))
        path, fname = os.path.split(uri)
        mname, _ = os.path.splitext(fname)
        no_ext = os.path.join(path, mname)
        if os.path.exists(no_ext + '.pyc'):
            return imp.load_compiled(mname, no_ext + '.pyc')
        if os.path.exists(no_ext + '.py'):
            return imp.load_source(mname, no_ext + '.py')
        return None

    def execute(self, metadata):
        self.job_db.create_job_id()
        try:
            self.test_params()
        except Exception as e:
            self.terminate()
            raise e
        self.job_db.record_workload_params(metadata)
        self._setup_metadata(metadata)
        self._workload_thread = Thread(target=self.execute_workloads,
                                       args=(),
                                       name="Workload thread")
        self._workload_thread.start()
        # seems to be hanging here
        return self.job_db.job_id

    def terminate(self):
        self._terminated = True
        self.end_time = time.time()
        return self.terminate_current_run()

    def terminate_current_run(self):
        self.logger.info("Terminating current run")
        terminated_hosts = []
        for workload in self._workload_executors:
            workload.terminate()
            terminated_hosts.append(workload.remote_host)
        return terminated_hosts

    def test_params(self):
        workloads = self._create_workload_matrix()
        for current_workload in workloads:
            workload = current_workload['workload']
            self.logger.info("Testing FIO parameters for %s"
                             % current_workload)
            result = self._execute_workload(current_workload,
                                            workload,
                                            parse_only=True)
            if result:
                message = result[0]
                self.logger.error("FIO parameter validation failed")
                raise Exception("Workload parameter validation failed %s"
                                % message)
        pass

    def _execute_workload(self, current_workload, workload, parse_only=False):
        workload.options['iodepth'] = str(current_workload['queue-depth'])
        workload.options['bs'] = str(current_workload['blocksize'])
        slave_threads = []
        thread_pool = ThreadPool(processes=len(self.slaves) *
                                 self.volume_count)

        for slave in self.slaves:
            volume_number = 0
            while volume_number < self.volume_count:
                slave_workload = copy.copy(current_workload['workload'])
                slave_workload.remote_host = slave
                last_char_of_filename = chr(
                    ord(slave_workload.filename[-1:]) + volume_number)
                slave_workload.filename = ("%s%s" %
                                           (slave_workload.filename[:-1],
                                            last_char_of_filename))
                self.logger.debug("Device to profile on %s: %s" %
                                  (slave, slave_workload.filename))
                self._workload_executors.append(slave_workload)

                worker = thread_pool.apply_async(
                    self.execute_on_node, (slave_workload, parse_only))
                slave_threads.append(worker)
                volume_number += 1

        final_result = None
        for slave_thread in slave_threads:
            self.logger.debug("Waiting on %s" % slave_thread)
            result = slave_thread.get()
            self.logger.debug("Done waiting for %s, exit status %s" %
                              (slave_thread, result))
            if result:
                final_result = result
        return final_result

    def execute_workloads(self):
        self._terminated = False
        self.logger.info("Starting job %s" % (self.job_db.job_id))
        data_handler = DataHandler()
        self.register(data_handler.data_event)

        self.start_time = time.time()

        self.workload_status = {}

        workloads = self._create_workload_matrix()

        for current_workload in workloads:
            if self._terminated:
                continue

            workload = current_workload['workload']
            self._thread_gate = ThreadGate(len(self.slaves),
                                           workload.options['status-interval'])

            self.current_workload = current_workload['name']

            self.logger.info("Starting run %s" % self.current_workload)
            self.workload_status[self.current_workload] = "Running"

            scheduler = sched.scheduler(time.time, time.sleep)
            if self.deadline is not None \
                    and not current_workload['workload_name'].startswith("_"):
                event = scheduler.enter(self.deadline * 60, 1,
                                        self.terminate_current_run,
                                        ())
                t = Thread(target=scheduler.run, args=())
                t.start()

            self._execute_workload(current_workload, workload)

            if not scheduler.empty():
                try:
                    scheduler.cancel(event)
                except ValueError:
                    pass

            self.logger.info("Completed run %s"
                             % self.current_workload)
            self.workload_status[self.current_workload] = "Completed"
            self._workload_executors = []
            self.current_workload = None

        self.logger.info("Completed job %s" % (self.job_db.job_id))

        self.end_time = time.time()
        self._terminated = True
        self.broadcast_event()
        self.unregister(data_handler.data_event)
        report = {'report': json.dumps(self.metadata)}
        self.job_db.record_workload_params(report)
        self.job_db.job_id = None

    def _create_workload_matrix(self):
        workloads = []

        if self._custom_workloads:
            for workload_name in self._custom_workloads.iterkeys():
                if not workload_name.isalnum():
                    raise InvalidWorkloadName(
                        "Workload name must be alphanumeric only: %s" %
                        workload_name)
                workload = _custom_workload()
                workload.options['name'] = workload_name
                workload.name = workload_name
                if (self.filename is not None):
                    workload.filename = self.filename
                workload.id = self.job_db.job_id

                workload_params = self._custom_workloads[workload_name]
                for param, value in workload_params.iteritems():
                    if param == "readwrite":
                        param = "rw"
                    if param in workload.fixed_options:
                        self.logger.warn("Skipping fixed option %s" % param)
                        continue
                    workload.options[param] = value

                for blocksize in self._block_sizes:
                    for iodepth in self._queue_depths:

                        name = '%s.%s.queue-depth.%s.block-size.%s' % \
                            (self.job_db.job_id, workload_name, iodepth,
                             blocksize)
                        self.workload_status[name] = "Pending"

                        workload.options['bs'] = blocksize
                        workload.options['iodepth'] = iodepth

                        parameters = {'queue-depth': iodepth,
                                      'blocksize': blocksize,
                                      'name': name,
                                      'workload_name': workload_name,
                                      'status': 'Pending',
                                      'workload': workload}

                        self.logger.info("Workload %s=%s" %
                                         (name, workload.options))

                        workloads.append(parameters)
        else:
            for workload_module in self.workload_modules:
                workload_name = getattr(workload_module, "__name__")

                constructorMethod = getattr(workload_module, workload_name)
                workload = constructorMethod()
                if (self.filename is not None):
                    workload.filename = self.filename
                workload.id = self.job_db.job_id

                if (workload_name.startswith("_")):
                    iodepths = [8, ]
                    blocksizes = [16384, ]
                else:
                    iodepths = self._queue_depths
                    blocksizes = self._block_sizes

                for blocksize in blocksizes:
                    for iodepth in iodepths:

                        name = '%s.%s.queue-depth.%s.block-size.%s' % \
                            (self.job_db.job_id, workload_name, iodepth,
                             blocksize)
                        self.workload_status[name] = "Pending"

                        parameters = {'queue-depth': iodepth,
                                      'blocksize': blocksize,
                                      'name': name,
                                      'workload_name': workload_name,
                                      'status': 'Pending',
                                      'workload': workload}

                        self.logger.info("Workload %s=%s" % (name, parameters))

                        workloads.append(parameters)

        return workloads

    def execute_on_node(self, workload, parse_only=False):

        invoker = FIOInvoker(self.metadata)
        workload.invoker = invoker

        self.logger.info("Starting " + workload.fullname)

        if not parse_only:
            invoker.register(self.event)
            self.job_db.start_workload(workload)
        result = workload.execute(parse_only)
        if not parse_only:
            self.job_db.end_workload(workload)
            invoker.unregister(self.event)

        self.logger.info("Ended " + workload.fullname)
        return result
