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
from storperf.db.configuration_db import ConfigurationDB
from storperf.db.job_db import JobDB
from storperf.test_executor import TestExecutor
from threading import Thread
from time import sleep

from cinderclient import client as cinderclient
import heatclient.client as heatclient
from keystoneauth1 import loading
from keystoneauth1 import session
import paramiko
from scp import SCPClient


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
        job_id = self._test_executor.execute(params)

        return job_id

    def terminate_workloads(self):
        return self._test_executor.terminate()

    def fetch_results(self, job_id):
        if self._test_executor.job_db.job_id == job_id:
            return self._test_executor.metadata['metrics']

        workload_params = self.job_db.fetch_workload_params(job_id)
        if 'report' in workload_params:
            report = workload_params['report']
            return report['metrics']
        return {}

    def fetch_metadata(self, job_id):
        return self.job_db.fetch_workload_params(job_id)

    def fetch_job_status(self, job_id):
        return self._test_executor.execution_status(job_id)

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
        ssh.connect(slave, username='storperf',
                    key_filename='storperf/resources/ssh/storperf_rsa',
                    timeout=2)

        scp = SCPClient(ssh.get_transport())
        logger.debug("Transferring libaio.so.1 to %s" % slave)
        scp.put('/lib/x86_64-linux-gnu/libaio.so.1', '~/')
        logger.debug("Transferring fio to %s" % slave)
        scp.put('/usr/local/bin/fio', '~/')

        cmd = 'sudo cp -v libaio.so.1 /lib/x86_64-linux-gnu/libaio.so.1'
        logger.debug("Executing on %s: %s" % (slave, cmd))
        (_, stdout, stderr) = ssh.exec_command(cmd)

        for line in stdout.readlines():
            logger.debug(line.strip())
        for line in stderr.readlines():
            logger.error(line.strip())

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
            sess = session.Session(auth=auth)

            self.logger.debug("Looking up orchestration endpoint")
            heat_endpoint = sess.get_endpoint(auth=auth,
                                              service_type="orchestration",
                                              endpoint_type='publicURL')

            self.logger.debug("Orchestration endpoint is %s" % heat_endpoint)
            token = sess.get_token(auth=auth)

            self._heat_client = heatclient.Client(
                "1",
                endpoint=heat_endpoint,
                token=token)

            self.logger.debug("Creating cinder client")
            self._cinder_client = cinderclient.Client("2", session=sess)
            self.logger.debug("OpenStack authentication complete")
