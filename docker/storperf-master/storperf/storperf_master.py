##############################################################################
# Copyright (c) 2016 EMC and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

import StringIO
from datetime import datetime
import json
import logging
from multiprocessing.pool import ThreadPool
import os
import socket
from time import sleep
import uuid

import paramiko
from scp import SCPClient
from snaps.config.stack import StackConfig
from snaps.openstack.create_stack import OpenStackHeatStack
from snaps.openstack.os_credentials import OSCreds
from snaps.openstack.utils import heat_utils, cinder_utils, glance_utils
from snaps.thread_utils import worker_pool

from storperf.db.job_db import JobDB
from storperf.test_executor import TestExecutor


class ParameterError(Exception):
    """ """


class StorPerfMaster(object):

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        self.reset_values()

        self.job_db = JobDB()
        self.stack_settings = StackConfig(
            name=self.stack_name,
            template_path='storperf/resources/hot/agent-group.yaml')

        self.os_creds = OSCreds(
            username=os.environ.get('OS_USERNAME'),
            password=os.environ.get('OS_PASSWORD'),
            auth_url=os.environ.get('OS_AUTH_URL'),
            identity_api_version=os.environ.get('OS_IDENTITY_API_VERSION'),
            user_domain_name=os.environ.get('OS_USER_DOMAIN_NAME'),
            user_domain_id=os.environ.get('OS_USER_DOMAIN_ID'),
            region_name=os.environ.get('OS_REGION_NAME'),
            project_domain_name=os.environ.get('OS_PROJECT_DOMAIN_NAME'),
            project_domain_id=os.environ.get('OS_PROJECT_DOMAIN_ID'),
            project_name=os.environ.get('OS_PROJECT_NAME'))

        self.logger.debug("OSCreds: %s" % self.os_creds)

        self.heat_stack = OpenStackHeatStack(self.os_creds,
                                             self.stack_settings)

        self._snaps_pool = worker_pool(20)

    def reset_values(self):
        self._stack_name = 'StorPerfAgentGroup'
        self.username = None
        self.password = None
        self._ssh_key = None
        self._test_executor = None
        self._agent_count = 1
        self._agent_image = None
        self._agent_flavor = None
        self._availability_zone = None
        self._public_network = None
        self._volume_count = 1
        self._volume_size = 1
        self._volume_type = None
        self._slave_addresses = []
        self._filename = None
        self._deadline = None
        self._steady_state_samples = 10
        self._queue_depths = "1"
        self._block_sizes = "4096"
        self._workload_modules = []
        self._custom_workloads = []
        self._subnet_CIDR = '172.16.0.0/16'
        self.slave_info = {}
        self.stackless = False
        self.mkfs = None
        self.mount_device = None
        self._last_snaps_check_time = None
        self._cached_stack_id = None

    @property
    def volume_count(self):
        self._get_stack_info()
        return self._volume_count

    @volume_count.setter
    def volume_count(self, value):
        if (self.stack_id is not None):
            raise ParameterError(
                "ERROR: Cannot change volume count after stack is created")
        self._volume_count = value

    @property
    def volume_size(self):
        self._get_stack_info()
        return self._volume_size

    @volume_size.setter
    def volume_size(self, value):
        if (self.stack_id is not None):
            raise ParameterError(
                "ERROR: Cannot change volume size after stack is created")
        self._volume_size = value

    @property
    def volume_type(self):
        self._get_stack_info()
        return self._volume_type

    @volume_type.setter
    def volume_type(self, value):
        if (self.stack_id is not None):
            raise ParameterError(
                "ERROR: Cannot change volume type after stack is created")
        self._volume_type = value

    @property
    def stack_name(self):
        return self._stack_name

    @stack_name.setter
    def stack_name(self, value):
        if value is None:
            self.stackless = True
        else:
            self.stackless = False
            self._stack_name = value
            self.stack_settings.name = self.stack_name
            self.stack_id = None
            self._last_snaps_check_time = None

    @property
    def subnet_CIDR(self):
        return self._subnet_CIDR

    @subnet_CIDR.setter
    def subnet_CIDR(self, value):
        if (self.stack_id is not None):
            raise ParameterError(
                "ERROR: Cannot change subnet CIDR after stack is created")
        self._subnet_CIDR = value

    @property
    def agent_count(self):
        self._get_stack_info()
        return self._agent_count

    @agent_count.setter
    def agent_count(self, value):
        if (self.stack_id is not None):
            raise ParameterError(
                "ERROR: Cannot change agent count after stack is created")
        self._agent_count = value

    @property
    def agent_image(self):
        self._get_stack_info()
        return self._agent_image

    @agent_image.setter
    def agent_image(self, value):
        if (self.stack_id is not None):
            raise ParameterError(
                "ERROR: Cannot change agent image after stack is created")
        self._agent_image = value

    @property
    def public_network(self):
        self._get_stack_info()
        return self._public_network

    @public_network.setter
    def public_network(self, value):
        if (self.stack_id is not None):
            raise ParameterError(
                "ERROR: Cannot change public network after stack is created")
        self._public_network = value

    @property
    def agent_flavor(self):
        self._get_stack_info()
        return self._agent_flavor

    @agent_flavor.setter
    def agent_flavor(self, value):
        if (self.stack_id is not None):
            raise ParameterError(
                "ERROR: Cannot change flavor after stack is created")
        self._agent_flavor = value

    @property
    def slave_addresses(self):
        return self._slave_addresses

    @slave_addresses.setter
    def slave_addresses(self, value):
        self._slave_addresses = value

    @property
    def stack_id(self):
        self._get_stack_info()
        return self._cached_stack_id

    @stack_id.setter
    def stack_id(self, value):
        self._cached_stack_id = value

    def _get_stack_info(self):
        if self.stackless:
            self._cached_stack_id = None
            return None

        if self._last_snaps_check_time is not None:
            time_since_check = datetime.now() - self._last_snaps_check_time
            if time_since_check.total_seconds() < 60:
                return self._cached_stack_id

        self.heat_stack.initialize()

        if self.heat_stack.get_stack() is not None:
            self._cached_stack_id = self.heat_stack.get_stack().id
            cinder_cli = cinder_utils.cinder_client(self.os_creds)
            glance_cli = glance_utils.glance_client(self.os_creds)

            router_worker = self._snaps_pool.apply_async(
                self.heat_stack.get_router_creators)

            vm_inst_creators = self.heat_stack.get_vm_inst_creators()
            self._agent_count = len(vm_inst_creators)
            vm1 = vm_inst_creators[0]
            self._availability_zone = \
                vm1.instance_settings.availability_zone
            self._agent_flavor = vm1.instance_settings.flavor.name

            self._slave_addresses = []
            for instance in vm_inst_creators:
                floating_ip = instance.get_floating_ip()
                self._slave_addresses.append(floating_ip.ip)
                self.logger.debug("Found VM at %s" % floating_ip.ip)

            server = vm1.get_vm_inst()

            image_worker = self._snaps_pool.apply_async(
                glance_utils.get_image_by_id, (glance_cli, server.image_id))

            self._volume_count = len(server.volume_ids)
            if self._volume_count > 0:
                volume_id = server.volume_ids[0]['id']
                volume = cinder_utils.get_volume_by_id(
                    cinder_cli, volume_id)
                self.logger.debug("Volume id %s, size=%s, type=%s" %
                                  (volume.id,
                                   volume.size,
                                   volume.type))
                self._volume_size = volume.size
                self._volume_type = volume.type

            image = image_worker.get()
            self._agent_image = image.name

            router_creators = router_worker.get()
            router1 = router_creators[0]
            self._public_network = \
                router1.router_settings.external_gateway

            self._last_snaps_check_time = datetime.now()
        else:
            self._cached_stack_id = None

        return self._cached_stack_id

    @property
    def availability_zone(self):
        self._get_stack_info()
        return self._availability_zone

    @availability_zone.setter
    def availability_zone(self, value):
        if (self.stack_id is not None):
            raise ParameterError(
                "ERROR: Cannot change zone after stack is created")
        self._availability_zone = value

    @property
    def volume_quota(self):
        # (TODO) Use SNAPS equivalent for Volume Quotas
        pass

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, value):
        self._filename = value

    @property
    def deadline(self):
        return self._deadline

    @deadline.setter
    def deadline(self, value):
        self._deadline = value

    @property
    def steady_state_samples(self):
        return self._steady_state_samples

    @steady_state_samples.setter
    def steady_state_samples(self, value):
        self._steady_state_samples = value

    @property
    def queue_depths(self):
        return self._queue_depths

    @queue_depths.setter
    def queue_depths(self, value):
        self._queue_depths = value

    @property
    def block_sizes(self):
        return self._block_sizes

    @block_sizes.setter
    def block_sizes(self, value):
        self._block_sizes = value

    @property
    def workloads(self):
        return self._workload_modules

    @workloads.setter
    def workloads(self, value):
        executor = TestExecutor()
        executor.register_workloads(value)
        self._workload_modules = value

    @property
    def custom_workloads(self):
        return self._custom_workloads

    @custom_workloads.setter
    def custom_workloads(self, value):
        self.logger.info("Custom workloads = %s" % value)
        self._custom_workloads = value

    @property
    def ssh_key(self):
        if self._ssh_key is None:
            return None
        key = StringIO.StringIO(self._ssh_key)
        pkey = paramiko.RSAKey.from_private_key(key)
        key.close()
        return pkey

    @ssh_key.setter
    def ssh_key(self, value):
        self._ssh_key = value

    @property
    def is_stack_created(self):
        return (self.stack_id is not None and
                (self.heat_stack.get_status() == u'CREATE_COMPLETE' or
                 self.heat_stack.get_status() == u'UPDATE_COMPLETE'))

    def get_logs(self, lines=None):
        LOG_DIR = './storperf.log'

        if isinstance(lines, int):
            logs = []
            index = 0
            for line in reversed(open(LOG_DIR).readlines()):
                if index != int(lines):
                    logs.insert(0, line.strip())
                    index += 1
                else:
                    break
        else:
            with open(LOG_DIR) as f:
                logs = f.read().split('\n')
        return logs

    def create_stack(self):
        self.stackless = False

        self.stack_settings.resource_files = [
            'storperf/resources/hot/storperf-agent.yaml',
            'storperf/resources/hot/storperf-volume.yaml']
        self.stack_settings.env_values = self._make_parameters()
        try:
            self.heat_stack.create(block=True)
        except Exception as e:
            self.logger.error("Stack creation failed")
            self.logger.exception(e)
            heat_cli = heat_utils.heat_client(self.os_creds)
            if self.heat_stack.get_stack() is not None:
                res = heat_utils.get_resources(heat_cli,
                                               self.heat_stack.get_stack().id)
                reason = ""
                failed = False
                for resource in res:
                    if resource.status == u'CREATE_FAILED':
                        failed = True
                        reason += "%s: %s " % (resource.name,
                                               resource.status_reason)
                    self.logger.error("%s - %s: %s" % (resource.name,
                                                       resource.status,
                                                       resource.status_reason))

                if failed:
                    try:
                        self.heat_stack.clean()
                    except Exception:
                        pass
                    raise Exception(reason)
            else:
                raise e

    def delete_stack(self):
        if self._test_executor is not None:
            self._test_executor.terminate()

        stack_id = None
        if (self.stack_id is not None):
            stack_id = self.stack_id
            try:
                self.heat_stack.clean()
            except Exception as e:
                self.logger.error("Stack creation failed")
                raise Exception(e)
            self.stack_id = None
        return stack_id

    def executor_event(self, executor):
        if executor.terminated:
            self._test_executor = None

    def execute_workloads(self, metadata={}):
        if (self._test_executor is not None and
                (not self._test_executor.terminated and
                 self._test_executor.job_id is not None)):
            raise Exception("ERROR: Job {} is already running".format(
                self._test_executor.job_id))

        if (not self.stackless and
                self.stack_id is None):
            raise ParameterError("ERROR: Stack %s does not exist" %
                                 self.stack_name)

        self._test_executor = TestExecutor()
        self._test_executor.register(self.executor_event)
        self._test_executor.register_workloads(self._workload_modules)
        self._test_executor.custom_workloads = self.custom_workloads
        self._test_executor.block_sizes = self._block_sizes
        self._test_executor.filename = self._filename
        self._test_executor.deadline = self._deadline
        self._test_executor.steady_state_samples = self._steady_state_samples
        self._test_executor.queue_depths = self._queue_depths

        slaves = self._slave_addresses

        setup_pool = ThreadPool(processes=len(slaves))

        workers = []
        for slave in slaves:
            worker = setup_pool.apply_async(
                self._setup_slave, (slave,))
            workers.append(worker)

        for worker in workers:
            worker.get()

        setup_pool.close()

        self._test_executor.slaves = slaves
        self._test_executor.volume_count = self.volume_count
        params = metadata
        params['agent_count'] = len(slaves)
        params['agent_flavor'] = self.agent_flavor
        params['agent_image'] = self.agent_image
        params['agent_info'] = json.dumps(self.slave_info)
        params['avaiability_zone'] = self.availability_zone
        params['block_sizes'] = self.block_sizes
        params['deadline'] = self.deadline
        params['public_network'] = self.public_network
        params['stack_name'] = self.stack_name
        params['steady_state_samples'] = self.steady_state_samples
        params['subnet_CIDR'] = self.subnet_CIDR
        params['target'] = self.filename
        params['volume_count'] = self.volume_count
        params['volume_size'] = self.volume_size
        params['volume_type'] = self.volume_type
        if self.username:
            params['username'] = self.username
        if self.password:
            params['password'] = self.password
        if self.ssh_key:
            params['ssh_key'] = self.ssh_key
        job_id = self._test_executor.execute(params)
        self.slave_info = {}

        return job_id

    def terminate_workloads(self):
        if self._test_executor is not None:
            return self._test_executor.terminate()
        else:
            return True

    def fetch_results(self, job_id):
        if (self._test_executor is not None and
                self._test_executor.job_db.job_id == job_id):
            return self._test_executor.metadata['details']['metrics']

        workload_params = self.job_db.fetch_workload_params(job_id)
        if 'report' in workload_params:
            report = workload_params['report']
            return report['details']['metrics']
        return {}

    def fetch_metadata(self, job_id):
        return self.job_db.fetch_workload_params(job_id)

    def fetch_job_status(self, job_id):
        results = {}

        if (self._test_executor is not None and
                self._test_executor.job_id == job_id):
            results['Status'] = 'Running'
            results['Workloads'] = self._test_executor.workload_status
        else:
            jobs = self.job_db.fetch_jobs()
            for job in jobs:
                if job == job_id:
                    results['Status'] = "Completed"

        return results

    def fetch_all_jobs(self, metrics_type):
        job_list = self.job_db.fetch_jobs()
        job_report = {}
        if metrics_type is None:
            job_report['job_ids'] = job_list
        elif metrics_type == "metadata":
            job_report['results'] = []
            for job in job_list:
                if metrics_type == 'metadata':
                    metadata = self.fetch_metadata(job)
                    if 'report' in metadata:
                        metadata['report']['_id'] = job
                        job_report['results'].append(metadata['report'])
        return job_report

    def _setup_slave(self, slave):
        logger = logging.getLogger(__name__ + ":" + slave)

        logger.info("Initializing slave at " + slave)

        logger.debug("Checking if slave " + slave + " is alive")

        alive = False
        timer = 10
        while not alive:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = s.connect_ex((slave, 22))
            s.close()

            if result:
                alive = False
                sleep(1)
                timer -= 1
                if timer == 0:
                    logger.debug("Still waiting for slave " + slave)
                    timer = 10
            else:
                alive = True
                logger.debug("Slave " + slave + " is alive and ready")

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        if self.username and self.password:
            ssh.connect(
                slave,
                username=self.username,
                password=self.password,
                timeout=2)
        elif self.username and self.ssh_key:
            ssh.connect(
                slave,
                username=self.username,
                pkey=self.ssh_key,
                timeout=2)
        else:
            ssh.connect(
                slave,
                username='storperf',
                key_filename='storperf/resources/ssh/storperf_rsa',
                timeout=2)

        uname = self._get_uname(ssh)
        logger.debug("Slave uname is %s" % uname)
        self.slave_info[slave] = {}
        self.slave_info[slave]['uname'] = uname

        available = self._check_root_fs(ssh)
        logger.debug("Available space on / is %s" % available)
        if available < 65536:
            logger.warn("Root filesystem is too small, attemping resize")
            self._resize_root_fs(ssh, logger)

            available = self._check_root_fs(ssh)
            logger.debug("Available space on / is now %s" % available)
            if available < 65536:
                logger.error("Cannot create enough space on /")
                raise Exception("Root filesystem has only %s free" %
                                available)

        scp = SCPClient(ssh.get_transport())
        logger.debug("Transferring fio to %s" % slave)
        scp.put('/usr/local/bin/fio', '~/')

        if self.mkfs is not None:
            self._mkfs(ssh, logger)

        if self.mount_device is not None:
            self._mount(ssh, logger)

    def _get_uname(self, ssh):
        (_, stdout, _) = ssh.exec_command("uname -a")
        return stdout.readline()

    def _check_root_fs(self, ssh):
        (_, stdout, _) = ssh.exec_command("df /")
        stdout.readline()
        lines = stdout.readline().split()
        if len(lines) > 4:
            available = lines[3]
            return int(available)

    def _mkfs(self, ssh, logger):
        command = "sudo umount %s" % (self.mount_device)
        logger.info("Attempting %s" % command)
        (_, stdout, stderr) = ssh.exec_command(command)
        stdout.channel.recv_exit_status()
        for line in iter(stdout.readline, b''):
            logger.info(line)
        for line in iter(stderr.readline, b''):
            logger.error(line)

        command = "sudo mkfs.%s %s" % (self.mkfs, self.mount_device)
        logger.info("Attempting %s" % command)
        (_, stdout, stderr) = ssh.exec_command(command)
        rc = stdout.channel.recv_exit_status()
        stdout.channel.recv_exit_status()
        for line in iter(stdout.readline, b''):
            logger.info(line)
        error_messages = ""
        for line in iter(stderr.readline, b''):
            logger.error(line)
            error_messages += line.rstrip()

        if rc != 0:
            raise Exception(
                "Error executing on {0}: {1}".format(
                    command, error_messages))

    def _mount(self, ssh, logger):
        command = "sudo mkdir -p %s" % (self.filename)
        logger.info("Attempting %s" % command)
        (_, stdout, stderr) = ssh.exec_command(command)
        stdout.channel.recv_exit_status()
        for line in iter(stdout.readline, b''):
            logger.info(line)
        for line in iter(stderr.readline, b''):
            logger.error(line)

        command = "sudo mount %s %s" % (self.mount_device, self.filename)
        logger.info("Attempting %s" % command)
        (_, stdout, stderr) = ssh.exec_command(command)
        rc = stdout.channel.recv_exit_status()
        for line in iter(stdout.readline, b''):
            logger.info(line)
        error_messages = ""
        for line in iter(stderr.readline, b''):
            logger.error(line)
            error_messages += line.rstrip()

        if rc != 0:
            raise Exception(
                "Could not mount {0}: {1}".format(
                    self.mount_device, error_messages))

    def _resize_root_fs(self, ssh, logger):
        command = "sudo /usr/sbin/resize2fs /dev/vda1"
        logger.info("Attempting %s" % command)
        (_, stdout, stderr) = ssh.exec_command(command)
        stdout.channel.recv_exit_status()
        for line in iter(stdout.readline, b''):
            logger.info(line)
        for line in iter(stderr.readline, b''):
            logger.error(line)

    def _make_parameters(self):
        random_str = uuid.uuid4().hex[:6].upper()
        heat_parameters = {}
        heat_parameters['public_network'] = self.public_network
        heat_parameters['agent_count'] = self.agent_count
        heat_parameters['volume_count'] = self.volume_count
        heat_parameters['volume_size'] = self.volume_size
        heat_parameters['keypair_name'] = 'storperf_agent_keypair' + random_str
        heat_parameters['subnet_CIDR'] = self.subnet_CIDR
        if self.volume_type is not None:
            heat_parameters['volume_type'] = self.volume_type
        heat_parameters['agent_image'] = self.agent_image
        heat_parameters['agent_flavor'] = self.agent_flavor
        heat_parameters['availability_zone'] = self.availability_zone
        return heat_parameters
