##############################################################################
# Copyright (c) 2016 EMC and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

from datetime import datetime
import logging
import os
import socket
from threading import Thread
from time import sleep

from cinderclient import client as cinderclient
from keystoneauth1 import loading
from keystoneauth1 import session
import paramiko
from scp import SCPClient

import heatclient.client as heatclient
from storperf.db.configuration_db import ConfigurationDB
from storperf.db.job_db import JobDB
from storperf.test_executor import TestExecutor


class ParameterError(Exception):
    """ """


class StorPerfMaster(object):

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        self.configuration_db = ConfigurationDB()
        self.job_db = JobDB()

        template_file = open("storperf/resources/hot/agent-group.yaml")
        self._agent_group_hot = template_file.read()
        template_file = open("storperf/resources/hot/storperf-agent.yaml")
        self._agent_resource_hot = template_file.read()
        self._hot_files = {
            'storperf-agent.yaml': self._agent_resource_hot
        }
        self.logger.debug(
            "Loaded agent-group template as: " + self._agent_group_hot)
        self.logger.debug(
            "Loaded agent-resource template as: " + self._agent_resource_hot)

        self._cinder_client = None
        self._heat_client = None
        self._test_executor = TestExecutor()
        self._last_openstack_auth = datetime.now()

    @property
    def volume_size(self):
        value = self.configuration_db.get_configuration_value(
            'stack',
            'volume_size')
        if (value is None):
            self.volume_size = 1
            value = 1
        return int(value)

    @volume_size.setter
    def volume_size(self, value):
        if (self.stack_id is not None):
            raise ParameterError(
                "ERROR: Cannot change volume size after stack is created")

        self.configuration_db.set_configuration_value(
            'stack',
            'volume_size',
            value)

    @property
    def agent_count(self):
        value = self.configuration_db.get_configuration_value(
            'stack',
            'agent_count')

        if (value is None):
            self.agent_count = 1
            value = 1
        return int(value)

    @agent_count.setter
    def agent_count(self, value):
        if (self.stack_id is not None):
            raise ParameterError(
                "ERROR: Cannot change agent count after stack is created")

        self.configuration_db.set_configuration_value(
            'stack',
            'agent_count',
            value)

    @property
    def agent_image(self):
        value = self.configuration_db.get_configuration_value(
            'stack',
            'agent_image')

        if (value is None):
            value = 'Ubuntu 14.04'
            self.agent_image = value

        return value

    @agent_image.setter
    def agent_image(self, value):
        if (self.stack_id is not None):
            raise ParameterError(
                "ERROR: Cannot change agent image after stack is created")

        self.configuration_db.set_configuration_value(
            'stack',
            'agent_image',
            value)

    @property
    def public_network(self):
        return self.configuration_db.get_configuration_value(
            'stack',
            'public_network')

    @public_network.setter
    def public_network(self, value):
        if (self.stack_id is not None):
            raise ParameterError(
                "ERROR: Cannot change public network after stack is created")

        self.configuration_db.set_configuration_value(
            'stack',
            'public_network',
            value)

    @property
    def agent_flavor(self):
        return self.configuration_db.get_configuration_value(
            'stack',
            'agent_flavor')

    @agent_flavor.setter
    def agent_flavor(self, value):
        if (self.stack_id is not None):
            raise ParameterError(
                "ERROR: Cannot change flavor after stack is created")

        self.configuration_db.set_configuration_value(
            'stack',
            'agent_flavor',
            value)

    @property
    def stack_id(self):
        return self.configuration_db.get_configuration_value(
            'stack',
            'stack_id')

    @stack_id.setter
    def stack_id(self, value):
        self.configuration_db.set_configuration_value(
            'stack',
            'stack_id',
            value)

    @property
    def availability_zone(self):
        return self.configuration_db.get_configuration_value(
            'stack',
            'availability_zone')

    @availability_zone.setter
    def availability_zone(self, value):
        self.configuration_db.set_configuration_value(
            'stack',
            'availability_zone',
            value)

    @property
    def volume_quota(self):
        self._attach_to_openstack()
        quotas = self._cinder_client.quotas.get(
            os.environ.get('OS_TENANT_ID'))
        return int(quotas.volumes)

    @property
    def filename(self):
        return self._test_executor.filename

    @filename.setter
    def filename(self, value):
        self._test_executor.filename = value

    @property
    def deadline(self):
        return self._test_executor.deadline

    @deadline.setter
    def deadline(self, value):
        self._test_executor.deadline = value

    @property
    def steady_state_samples(self):
        return self._test_executor.steady_state_samples

    @steady_state_samples.setter
    def steady_state_samples(self, value):
        self._test_executor.steady_state_samples = value

    @property
    def queue_depths(self):
        return self._test_executor.queue_depths

    @queue_depths.setter
    def queue_depths(self, value):
        self._test_executor.queue_depths = value

    @property
    def block_sizes(self):
        return self._test_executor.block_sizes

    @block_sizes.setter
    def block_sizes(self, value):
        self._test_executor.block_sizes = value

    @property
    def is_stack_created(self):
        if (self.stack_id is not None):
            self._attach_to_openstack()

            stack = self._heat_client.stacks.get(self.stack_id)
            status = getattr(stack, 'stack_status')

            self.logger.info("Status=" + status)
            if (status == u'CREATE_COMPLETE'):
                return True

        return False

    @property
    def workloads(self):
        return self.configuration_db.get_configuration_value(
            'workload',
            'workloads')

    @workloads.setter
    def workloads(self, value):
        self._test_executor.register_workloads(value)

        self.configuration_db.set_configuration_value(
            'workload',
            'workloads',
            str(self._test_executor.workload_modules))

    @property
    def username(self):
        return self.configuration_db.get_configuration_value(
            'stack',
            'username'
        )

    @username.setter
    def username(self, value):
        self.configuration_db.set_configuration_value(
            'stack',
            'username',
            value
        )

    @property
    def password(self):
        return self.configuration_db.get_configuration_value(
            'stack',
            'password'
        )

    @password.setter
    def password(self, value):
        self.configuration_db.set_configuration_value(
            'stack',
            'password',
            value
        )

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
        if (self.stack_id is not None):
            raise ParameterError("ERROR: Stack has already been created")

        self._attach_to_openstack()
        volume_quota = self.volume_quota
        if (volume_quota > 0 and self.agent_count > volume_quota):
            message = "ERROR: Volume quota too low: " + \
                str(self.agent_count) + " > " + str(self.volume_quota)
            raise ParameterError(message)

        self.logger.debug("Creating stack")
        stack = self._heat_client.stacks.create(
            stack_name="StorPerfAgentGroup",
            template=self._agent_group_hot,
            files=self._hot_files,
            parameters=self._make_parameters())

        self.stack_id = stack['stack']['id']

        while True:
            stack = self._heat_client.stacks.get(self.stack_id)
            status = getattr(stack, 'stack_status')
            self.logger.debug("Stack status=%s" % (status,))
            if (status == u'CREATE_COMPLETE'):
                return True
            if (status == u'DELETE_COMPLETE'):
                self.stack_id = None
                return True
            if (status == u'CREATE_FAILED'):
                self.status_reason = getattr(stack, 'stack_status_reason')
                sleep(5)
                self._heat_client.stacks.delete(stack_id=self.stack_id)
            sleep(2)

    def delete_stack(self):
        if (self.stack_id is None):
            raise ParameterError("ERROR: Stack does not exist")

        self._attach_to_openstack()
        while True:
            stack = self._heat_client.stacks.get(self.stack_id)
            status = getattr(stack, 'stack_status')
            self.logger.debug("Stack status=%s" % (status,))
            if (status == u'CREATE_COMPLETE'):
                self._heat_client.stacks.delete(stack_id=self.stack_id)
            if (status == u'DELETE_COMPLETE'):
                self.stack_id = None
                return True
            if (status == u'DELETE_FAILED'):
                sleep(5)
                self._heat_client.stacks.delete(stack_id=self.stack_id)
            sleep(2)

    def execute_workloads(self, metadata={}):
        if (self.stack_id is None):
            raise ParameterError("ERROR: Stack does not exist")

        self._attach_to_openstack()

        stack = self._heat_client.stacks.get(self.stack_id)
        outputs = getattr(stack, 'outputs')
        slaves = outputs[0]['output_value']

        setup_threads = []

        for slave in slaves:
            t = Thread(target=self._setup_slave, args=(slave,))
            setup_threads.append(t)
            t.start()

        for thread in setup_threads:
            thread.join()

        self._test_executor.slaves = slaves

        params = metadata
        params['agent_count'] = self.agent_count
        params['public_network'] = self.public_network
        params['volume_size'] = self.volume_size
        if self.username and self.password:
            params['username'] = self.username
            params['password'] = self.password
        job_id = self._test_executor.execute(params)

        return job_id

    def terminate_workloads(self):
        return self._test_executor.terminate()

    def fetch_results(self, job_id):
        if self._test_executor.job_db.job_id == job_id:
            return self._test_executor.metadata['details']['metrics']

        workload_params = self.job_db.fetch_workload_params(job_id)
        if 'report' in workload_params:
            report = workload_params['report']
            return report['metrics']
        return {}

    def fetch_metadata(self, job_id):
        return self.job_db.fetch_workload_params(job_id)

    def fetch_job_status(self, job_id):
        return self._test_executor.execution_status(job_id)

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
                        metadata['report']['start_date'] = \
                            metadata['report']['start_time']
                        metadata['report']['end_date'] = \
                            metadata['report']['end_time']
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
            ssh.connect(slave,
                        username=self.username,
                        password=self.password)
        else:
            ssh.connect(slave, username='storperf',
                        key_filename='storperf/resources/ssh/storperf_rsa',
                        timeout=2)

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

    def _check_root_fs(self, ssh):
        (_, stdout, _) = ssh.exec_command("df /")
        stdout.readline()
        lines = stdout.readline().split()
        if len(lines) > 4:
            available = lines[3]
            return int(available)

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
        heat_parameters = {}
        heat_parameters['public_network'] = self.public_network
        heat_parameters['agent_count'] = self.agent_count
        heat_parameters['volume_size'] = self.volume_size
        heat_parameters['agent_image'] = self.agent_image
        heat_parameters['agent_flavor'] = self.agent_flavor
        return heat_parameters

    def _attach_to_openstack(self):

        time_since_last_auth = datetime.now() - self._last_openstack_auth

        if (self._heat_client is None or
                time_since_last_auth.total_seconds() > 600):
            self._last_openstack_auth = datetime.now()

            creds = {
                "username": os.environ.get('OS_USERNAME'),
                "password": os.environ.get('OS_PASSWORD'),
                "auth_url": os.environ.get('OS_AUTH_URL'),
                "project_domain_id":
                    os.environ.get('OS_PROJECT_DOMAIN_ID'),
                "project_domain_name":
                    os.environ.get('OS_PROJECT_DOMAIN_NAME'),
                "project_id": os.environ.get('OS_PROJECT_ID'),
                "project_name": os.environ.get('OS_PROJECT_NAME'),
                "tenant_name": os.environ.get('OS_TENANT_NAME'),
                "tenant_id": os.environ.get("OS_TENANT_ID"),
                "user_domain_id": os.environ.get('OS_USER_DOMAIN_ID'),
                "user_domain_name": os.environ.get('OS_USER_DOMAIN_NAME')
            }

            self.logger.debug("Creds: %s" % creds)

            loader = loading.get_plugin_loader('password')
            auth = loader.load_from_options(**creds)

            https_cacert = os.getenv('OS_CACERT', '')
            https_insecure = os.getenv('OS_INSECURE', '').lower() == 'true'

            self.logger.info("cacert=%s" % https_cacert)

            sess = session.Session(auth=auth,
                                   verify=(https_cacert or not https_insecure))

            self.logger.debug("Looking up orchestration endpoint")
            heat_endpoint = sess.get_endpoint(auth=auth,
                                              service_type="orchestration",
                                              endpoint_type='publicURL')

            self.logger.debug("Orchestration endpoint is %s" % heat_endpoint)

            self._heat_client = heatclient.Client(
                "1",
                endpoint=heat_endpoint,
                session=sess)

            self.logger.debug("Creating cinder client")
            self._cinder_client = cinderclient.Client("2", session=sess,
                                                      cacert=https_cacert)
            self.logger.debug("OpenStack authentication complete")
