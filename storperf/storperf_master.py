##############################################################################
# Copyright (c) 2015 EMC and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

from threading import Thread
import logging
import os
import subprocess

from db.configuration_db import ConfigurationDB
from test_executor import TestExecutor
import cinderclient.v2 as cinderclient
import heatclient.client as heatclient
import keystoneclient.v2_0 as ksclient


class ParameterError(Exception):
    """ """


class StorPerfMaster(object):

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        self.configuration_db = ConfigurationDB()

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

        self._username = os.environ.get('OS_USERNAME')
        self._password = os.environ.get('OS_PASSWORD')
        self._tenant_name = os.environ.get('OS_TENANT_NAME')
        self._tenant_id = os.environ.get('OS_TENANT_ID')
        self._project_name = os.environ.get('OS_PROJECT_NAME')
        self._auth_url = os.environ.get('OS_AUTH_URL')

        self._cinder_client = None
        self._heat_client = None
        self._test_executor = TestExecutor()

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
    def agent_network(self):
        return self.configuration_db.get_configuration_value(
            'stack',
            'agent_network')

    @agent_network.setter
    def agent_network(self, value):
        if (self.stack_id is not None):
            raise ParameterError(
                "ERROR: Cannot change agent network after stack is created")

        self.configuration_db.set_configuration_value(
            'stack',
            'agent_network',
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
        quotas = self._cinder_client.quotas.get(self._tenant_id)
        return int(quotas.volumes)

    @property
    def filename(self):
        return self._test_executor.filename

    @filename.setter
    def filename(self, value):
        self._test_executor.filename = value

    @property
    def precondition(self):
        return self._test_executor.precondition

    @precondition.setter
    def precondition(self, value):
        self._test_executor.precondition = value

    @property
    def warm_up(self):
        return self._test_executor.warm

    @warm_up.setter
    def warm_up(self, value):
        self._test_executor.warm = value

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
        if (self.agent_count > self.volume_quota):
            message = "ERROR: Volume quota too low: " + \
                str(self.agent_count) + " > " + str(self.volume_quota)
            raise ParameterError(message)

        stack = self._heat_client.stacks.create(
            stack_name="StorPerfAgentGroup",
            template=self._agent_group_hot,
            files=self._hot_files,
            parameters=self._make_parameters())

        self.stack_id = stack['stack']['id']

    def validate_stack(self):
        self._attach_to_openstack()
        if (self.agent_count > self.volume_quota):
            message = "ERROR: Volume quota too low: " + \
                str(self.agent_count) + " > " + str(self.volume_quota)
            self.logger.error(message)
            raise ParameterError(message)

        self._heat_client.stacks.preview(
            stack_name="StorPerfAgentGroup",
            template=self._agent_group_hot,
            files=self._hot_files,
            parameters=self._make_parameters())
        return True

    def wait_for_stack_creation(self):

        pass

    def delete_stack(self):
        if (self.stack_id is None):
            raise ParameterError("ERROR: Stack does not exist")

        self._attach_to_openstack()

        self._heat_client.stacks.delete(stack_id=self.stack_id)
        self.stack_id = None

    def execute_workloads(self):
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
        return self._test_executor.execute()

    def terminate_workloads(self):
        return self._test_executor.terminate()

    def _setup_slave(self, slave):
        logger = logging.getLogger(__name__ + ":" + slave)

        logger.info("Initializing slave at " + slave)

        args = ['scp', '-o', 'StrictHostKeyChecking=no',
                '-i', 'storperf/resources/ssh/storperf_rsa',
                '/lib/x86_64-linux-gnu/libaio.so.1',
                'storperf@' + slave + ":"]

        logger.debug(args)
        proc = subprocess.Popen(args,
                                universal_newlines=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)

        (stdout, stderr) = proc.communicate()
        if (len(stdout) > 0):
            logger.debug(stdout.decode('utf-8').strip())
        if (len(stderr) > 0):
            logger.error(stderr.decode('utf-8').strip())

        args = ['scp', '-o', 'StrictHostKeyChecking=no',
                '-i', 'storperf/resources/ssh/storperf_rsa',
                '/usr/local/bin/fio',
                'storperf@' + slave + ":"]

        logger.debug(args)
        proc = subprocess.Popen(args,
                                universal_newlines=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)

        (stdout, stderr) = proc.communicate()
        if (len(stdout) > 0):
            logger.debug(stdout.decode('utf-8').strip())
        if (len(stderr) > 0):
            logger.error(stderr.decode('utf-8').strip())

        args = ['ssh', '-o', 'StrictHostKeyChecking=no',
                '-i', 'storperf/resources/ssh/storperf_rsa',
                'storperf@' + slave,
                'sudo cp -v libaio.so.1 /lib/x86_64-linux-gnu/libaio.so.1'
                ]

        logger.debug(args)
        proc = subprocess.Popen(args,
                                universal_newlines=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)

        (stdout, stderr) = proc.communicate()
        if (len(stdout) > 0):
            logger.debug(stdout.decode('utf-8').strip())
        if (len(stderr) > 0):
            logger.error(stderr.decode('utf-8').strip())

    def _make_parameters(self):
        heat_parameters = {}
        heat_parameters['agent_network'] = self.agent_network
        heat_parameters['agent_count'] = self.agent_count
        heat_parameters['volume_size'] = self.volume_size
        return heat_parameters

    def _attach_to_openstack(self):

        if (self._cinder_client is None):
            self._cinder_client = cinderclient.Client(
                self._username, self._password, self._project_name,
                self._auth_url, service_type='volumev2')
            self._cinder_client.authenticate()

        if (self._heat_client is None):
            self._keystone_client = ksclient.Client(
                auth_url=self._auth_url,
                username=self._username,
                password=self._password,
                tenant_name=self._tenant_name)
            heat_endpoint = self._keystone_client.service_catalog.url_for(
                service_type='orchestration')
            self._heat_client = heatclient.Client(
                '1', endpoint=heat_endpoint,
                token=self._keystone_client.auth_token)
