##############################################################################
# Copyright (c) 2015 EMC and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

import json
import logging.config
import os
import sys

from flask import abort, Flask, request, jsonify
from flask_cors import CORS
from flask_restful import Resource, Api, fields
from flask_restful_swagger import swagger

from storperf.storperf_master import StorPerfMaster


class ReverseProxied(object):
    '''Wrap the application in this middleware and configure the
    front-end server to add these headers, to let you quietly bind
    this to a URL other than / and to an HTTP scheme that is
    different than what is used locally.

    In nginx:
    location /storperf/ {
        proxy_pass http://localhost:8085/;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Scheme $scheme;
        proxy_set_header X-Script-Name /storperf;
    }

    :param app: the WSGI application
    '''

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        script_name = environ.get('HTTP_X_SCRIPT_NAME', '')
        if script_name:
            environ['SCRIPT_NAME'] = script_name
            path_info = environ['PATH_INFO']
            if path_info.startswith(script_name):
                environ['PATH_INFO'] = path_info[len(script_name):]

        scheme = environ.get('HTTP_X_SCHEME', '')
        if scheme:
            environ['wsgi.url_scheme'] = scheme
        return self.app(environ, start_response)


app = Flask(__name__, static_url_path="")
CORS(app)
api = swagger.docs(Api(app), apiVersion='1.0')
app.wsgi_app = ReverseProxied(app.wsgi_app)

storperf = StorPerfMaster()


class Logs(Resource):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    @swagger.operation(
        notes="Fetch logs",
        parameters=[
            {
                "name": "lines",
                "description": "The number of lines to fetch",
                "required": "False",
                "type": "string",
                "allowedMultiple": "False",
                "paramType": "query"
            }
        ]
    )
    def get(self):
        lines = request.args.get('lines')
        if lines:
            try:
                lines = int(lines)
            except Exception:
                pass
        else:
            lines = 35
        return jsonify({'logs': storperf.get_logs(lines)})


@swagger.model
class ConfigurationRequestModel:
    resource_fields = {
        'agent_count': fields.Integer,
        'agent_flavor': fields.String,
        'agent_image': fields.String,
        'public_network': fields.String,
        'volume_count': fields.Integer,
        'volume_size': fields.Integer,
        'volume_type': fields.String,
        'availability_zone': fields.String,
        'subnet_CIDR': fields.String,
        'stack_name': fields.String,
        'username': fields.String,
        'password': fields.String
    }


@swagger.model
class ConfigurationResponseModel:
    resource_fields = {
        'agent_count': fields.Integer,
        'agent_flavor': fields.String,
        'agent_image': fields.String,
        'public_network': fields.String,
        'stack_created': fields.Boolean,
        'stack_id': fields.String,
        'volume_count': fields.Integer,
        'volume_size': fields.Integer,
        'volume_type': fields.String,
        'availability_zone': fields.String,
        'subnet_CIDR': fields.String,
        'stack_name': fields.String,
        'slave_addresses': fields.Nested
    }


class Configure(Resource):

    """Configuration API"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    @swagger.operation(
        notes='Fetch the current agent configuration',
        parameters=[
            {
                "name": "stack_name",
                "description": "The name of the stack to use, defaults to" +
                "StorPerfAgentGroup or the last stack named",
                "required": False,
                "type": "string",
                "allowMultiple": False,
                "paramType": "query"
            }],
        type=ConfigurationResponseModel.__name__
    )
    def get(self):
        stack_name = request.args.get('stack_name')
        if stack_name:
            storperf.stack_name = stack_name

        return jsonify({'agent_count': storperf.agent_count,
                        'agent_flavor': storperf.agent_flavor,
                        'agent_image': storperf.agent_image,
                        'public_network': storperf.public_network,
                        'volume_count': storperf.volume_count,
                        'volume_size': storperf.volume_size,
                        'volume_type': storperf.volume_type,
                        'stack_created': storperf.is_stack_created,
                        'availability_zone': storperf.availability_zone,
                        'subnet_CIDR': storperf.subnet_CIDR,
                        'stack_name': storperf.stack_name,
                        'slave_addresses': storperf.slave_addresses,
                        'stack_id': storperf.stack_id})

    @swagger.operation(
        notes='''Set the current agent configuration and create a stack in
        the controller.  Returns once the stack create is completed.''',
        parameters=[
            {
                "name": "configuration",
                "description": '''Configuration to be set. All parameters are
                optional, and will retain their previous value if not
                specified.  Volume size is in GB.
                ''',
                "required": True,
                "type": "ConfigurationRequestModel",
                "paramType": "body"
            }
        ],
        type=ConfigurationResponseModel.__name__
    )
    def post(self):
        if not request.json:
            abort(400, "ERROR: No data specified")

        try:
            # Note this must be first in order to be able to create
            # more than one stack in the same StorPerf instance.
            if ('stack_name' in request.json):
                storperf.stack_name = request.json['stack_name']
            if ('agent_count' in request.json):
                storperf.agent_count = request.json['agent_count']
            if ('agent_flavor' in request.json):
                storperf.agent_flavor = request.json['agent_flavor']
            if ('agent_image' in request.json):
                storperf.agent_image = request.json['agent_image']
            if ('public_network' in request.json):
                storperf.public_network = request.json['public_network']
            if ('volume_count' in request.json):
                storperf.volume_count = request.json['volume_count']
            if ('volume_size' in request.json):
                storperf.volume_size = request.json['volume_size']
            if ('volume_type' in request.json):
                storperf.volume_type = request.json['volume_type']
            if ('availability_zone' in request.json):
                storperf.availability_zone = request.json['availability_zone']
            if ('subnet_CIDR' in request.json):
                storperf.subnet_CIDR = request.json['subnet_CIDR']
            if ('username' in request.json):
                storperf.username = request.json['username']
            if ('password' in request.json):
                storperf.password = request.json['password']

            storperf.create_stack()
            if storperf.stack_id is None:
                abort(400, storperf.status_reason)

            return self.get()

        except Exception as e:
            self.logger.exception(e)
            abort(400, str(e))

    @swagger.operation(
        notes='Deletes the agent configuration and the stack',
        parameters=[
            {
                "name": "stack_name",
                "description": "The name of the stack to delete, defaults to" +
                "StorPerfAgentGroup or the last stack named",
                "required": False,
                "type": "string",
                "allowMultiple": False,
                "paramType": "query"
            }]
    )
    def delete(self):
        stack_name = request.args.get('stack_name')
        if stack_name:
            storperf.stack_name = stack_name
        try:
            return jsonify({'stack_id': storperf.delete_stack()})
        except Exception as e:
            self.logger.exception(e)
            abort(400, str(e))


@swagger.model
class WorkloadModel:
    resource_fields = {
        'target': fields.String,
        'deadline': fields.Integer,
        "steady_state_samples": fields.Integer,
        'workload': fields.String,
        'queue_depths': fields.String,
        'block_sizes': fields.String,
        'stack_name': fields.String
    }


@swagger.model
class WorkloadResponseModel:
    resource_fields = {
        'job_id': fields.String
    }


class Job(Resource):

    """Job API"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    @swagger.operation(
        notes='Fetch the metrics of the specified workload',
        parameters=[
            {
                "name": "id",
                "description": "The UUID of the workload in the format "
                "NNNNNNNN-NNNN-NNNN-NNNN-NNNNNNNNNNNN",
                "required": False,
                "type": "string",
                "allowMultiple": False,
                "paramType": "query"
            },
            {
                "name": "type",
                "description": "The type of metrics to report. May be "
                "metrics (default), metadata, or status",
                "required": False,
                "type": "string",
                "allowMultiple": False,
                "paramType": "query"
            }
        ],
        responseMessages=[
            {
                "code": 200,
                "message": "Workload ID found, response in JSON format"
            },
            {
                "code": 404,
                "message": "Workload ID not found"
            }
        ]
    )
    def get(self):

        workload_id = request.args.get('id')

        if workload_id:
            metrics_type = "metrics"
            if request.args.get('type'):
                metrics_type = request.args.get('type')

            if metrics_type == "metrics":
                return jsonify(storperf.fetch_results(workload_id))

            if metrics_type == "metadata":
                return jsonify(storperf.fetch_metadata(workload_id))

            if metrics_type == "status":
                return jsonify(storperf.fetch_job_status(workload_id))

        else:
            metrics_type = None
            if request.args.get('type'):
                metrics_type = request.args.get('type')

            if metrics_type == "status":
                return jsonify(storperf.fetch_job_status(workload_id))

            else:
                return jsonify(storperf.fetch_all_jobs(metrics_type))

    @swagger.operation(
        parameters=[
            {
                "name": "body",
                "description": """Start execution of a workload with the
following parameters:

"target": The target device to profile",

"deadline": if specified, the maximum duration in minutes
for any single test iteration.

"workload":if specified, the workload to run. Defaults to all.

"stack_name": The target stack to use.  Defaults to StorPerfAgentGroup, or
the last stack named.
                """,
                "required": True,
                "type": "WorkloadModel",
                "paramType": "body"
            }
        ],
        type=WorkloadResponseModel.__name__,
        responseMessages=[
            {
                "code": 200,
                "message": "Job submitted"
            },
            {
                "code": 400,
                "message": "Missing configuration data"
            }
        ]
    )
    def post(self):
        if not request.json:
            abort(400, "ERROR: Missing configuration data")

        storperf.reset_values()
        self.logger.info(request.json)

        try:
            if ('stack_name' in request.json):
                storperf.stack_name = request.json['stack_name']
                storperf.stackless = False
            if ('target' in request.json):
                storperf.filename = request.json['target']
            if ('deadline' in request.json):
                storperf.deadline = request.json['deadline']
            if ('steady_state_samples' in request.json):
                storperf.steady_state_samples = request.json[
                    'steady_state_samples']
            if ('queue_depths' in request.json):
                storperf.queue_depths = request.json['queue_depths']
            if ('block_sizes' in request.json):
                storperf.block_sizes = request.json['block_sizes']
            storperf.workloads = None
            storperf.custom_workloads = None
            if ('workload' in request.json):
                storperf.workloads = request.json['workload']
            if ('metadata' in request.json):
                metadata = request.json['metadata']
            else:
                metadata = {}

            job_id = storperf.execute_workloads(metadata)

            return jsonify({'job_id': job_id})

        except Exception as e:
            self.logger.exception(e)
            abort(400, str(e))

    @swagger.operation(
        notes='Cancels the currently running workload',
        responseMessages=[
            {
                "code": 200,
                "message": "Wordload ID found, response in JSON format"
            },
        ]
    )
    def delete(self):
        self.logger.info("Threads: %s" % sys._current_frames())
        try:
            return jsonify({'Slaves': storperf.terminate_workloads()})
        except Exception as e:
            abort(400, str(e))


@swagger.model
class WorkloadsBodyModel:
    resource_fields = {
        "rw": fields.String(default="randrw")
    }
    required = ['rw']


@swagger.model
@swagger.nested(
    name=WorkloadsBodyModel.__name__)
class WorkloadsNameModel:
    resource_fields = {
        "name": fields.Nested(WorkloadsBodyModel.resource_fields)
    }


@swagger.model
@swagger.nested(
    workloads=WorkloadsNameModel.__name__)
class WorkloadV2Model:
    resource_fields = {
        'target': fields.String,
        'deadline': fields.Integer,
        "steady_state_samples": fields.Integer,
        'workloads': fields.Nested(WorkloadsNameModel.resource_fields),
        'queue_depths': fields.String,
        'block_sizes': fields.String,
        'stack_name': fields.String,
        'username': fields.String,
        'password': fields.String,
        'ssh_private_key': fields.String,
        'slave_addresses': fields.List
    }
    required = ['workloads']


class Job_v2(Resource):

    """Job API"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    @swagger.operation(
        parameters=[
            {
                "name": "body",
                "description": """Start execution of a workload with the
following parameters:

"target": The target device to profile",

"deadline": if specified, the maximum duration in minutes
for any single test iteration.

"workloads": A JSON formatted map of workload names and parameters for FIO.

"stack_name": The target stack to use.  Defaults to StorPerfAgentGroup, or
the last stack named.  Explicitly specifying null will bypass all Heat Stack
operations and go directly against the IP addresses specified.

"username": if specified, the username to use when logging into the slave.

"password": if specified, the password to use when logging into the slave.

"ssh_private_key": if specified, the ssh private key to use when logging
into the slave.

"slave_addresses": if specified, a list of IP addresses to use instead of
looking all of them up from the stack.

                """,
                "required": True,
                "type": "WorkloadV2Model",
                "paramType": "body"
            }
        ],
        type=WorkloadResponseModel.__name__,
        responseMessages=[
            {
                "code": 200,
                "message": "Job submitted"
            },
            {
                "code": 400,
                "message": "Missing configuration data"
            }
        ]
    )
    def post(self):
        if not request.json:
            abort(400, "ERROR: Missing job data")

        self.logger.info(request.json)
        storperf.reset_values()

        try:
            if ('stack_name' in request.json):
                storperf.stack_name = request.json['stack_name']
            if ('target' in request.json):
                storperf.filename = request.json['target']
            if ('deadline' in request.json):
                storperf.deadline = request.json['deadline']
            if ('steady_state_samples' in request.json):
                storperf.steady_state_samples = request.json[
                    'steady_state_samples']
            if ('queue_depths' in request.json):
                storperf.queue_depths = request.json['queue_depths']
            if ('block_sizes' in request.json):
                storperf.block_sizes = request.json['block_sizes']
            storperf.workloads = None
            storperf.custom_workloads = None
            if ('workload' in request.json):
                storperf.workloads = request.json['workload']
            if ('workloads' in request.json):
                storperf.custom_workloads = request.json['workloads']
            if ('metadata' in request.json):
                metadata = request.json['metadata']
            else:
                metadata = {}

            if 'username' in request.json:
                storperf.username = request.json['username']
            if 'password' in request.json:
                storperf.password = request.json['password']
            if 'ssh_private_key' in request.json:
                storperf.ssh_key = request.json['ssh_private_key']
            if 'slave_addresses' in request.json:
                storperf.slave_addresses = request.json['slave_addresses']

            job_id = storperf.execute_workloads(metadata)

            return jsonify({'job_id': job_id})

        except Exception as e:
            self.logger.exception(e)
            abort(400, str(e))


@swagger.model
class WarmUpModel:
    resource_fields = {
        'stack_name': fields.String,
        'target': fields.String,
        'username': fields.String,
        'password': fields.String,
        'ssh_private_key': fields.String,
        'slave_addresses': fields.List,
        'mkfs': fields.String,
        'mount_point': fields.String,
        'file_size': fields.String,
        'file_count': fields.String
    }


class Initialize(Resource):

    """Disk initialization API"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    @swagger.operation(
        parameters=[
            {
                "name": "body",
                "description": """Fill the target with random data.  If no
target is specified, it will default to /dev/vdb

"target": The target device to use.

"stack_name": The target stack to use.  Defaults to StorPerfAgentGroup, or
the last stack named.  Explicitly specifying null will bypass all Heat Stack
operations and go directly against the IP addresses specified.

"username": if specified, the username to use when logging into the slave.

"password": if specified, the password to use when logging into the slave.

"ssh_private_key": if specified, the ssh private key to use when logging
into the slave.

"slave_addresses": if specified, a list of IP addresses to use instead of
looking all of them up from the stack.

"mkfs": if specified, the command to execute in order to create a filesystem
on the target device (eg: mkfs.ext4)

"mount_point": if specified, the directory to use when mounting the device.

"filesize": if specified, the size of the files to create when profiling
a filesystem.

"nrfiles": if specified, the number of files to create when profiling
a filesystem

"numjobs": if specified, the number of jobs for when profiling
a filesystem
                """,
                "required": False,
                "type": "WarmUpModel",
                "paramType": "body"
            }
        ],
        type=WorkloadResponseModel.__name__,
        notes='''Initialize the target device or file by filling it to
        capacity with random data.  This is similar to the jobs API,
        but does not have a deadline or steady state.  It also
        uses a predefined block size and queue depth.''',
        responseMessages=[
            {
                "code": 200,
                "message": "Job submitted"
            },
            {
                "code": 400,
                "message": "Missing configuration data"
            }
        ]
    )
    def post(self):
        self.logger.info(request.json)
        storperf.reset_values()

        try:
            warm_up_args = {
                'rw': 'randwrite',
                'direct': "1",
                'loops': "1"
            }
            storperf.queue_depths = "8"
            storperf.block_sizes = "16k"

            if request.json:
                if 'target' in request.json:
                    storperf.filename = request.json['target']
                if 'stack_name' in request.json:
                    storperf.stack_name = request.json['stack_name']
                if 'username' in request.json:
                    storperf.username = request.json['username']
                if 'password' in request.json:
                    storperf.password = request.json['password']
                if 'ssh_private_key' in request.json:
                    storperf.ssh_key = request.json['ssh_private_key']
                if 'slave_addresses' in request.json:
                    storperf.slave_addresses = request.json['slave_addresses']
                if 'mkfs' in request.json:
                    storperf.mkfs = request.json['mkfs']
                if 'mount_device' in request.json:
                    storperf.mount_device = request.json['mount_device']
                if 'filesize' in request.json:
                    warm_up_args['filesize'] = str(request.json['filesize'])
                if 'nrfiles' in request.json:
                    warm_up_args['nrfiles'] = str(request.json['nrfiles'])
                if 'numjobs' in request.json:
                    warm_up_args['numjobs'] = str(request.json['numjobs'])

            storperf.workloads = None
            storperf.custom_workloads = {
                '_warm_up': warm_up_args
            }
            self.logger.info(storperf.custom_workloads)
            job_id = storperf.execute_workloads()

            return jsonify({'job_id': job_id})

        except Exception as e:
            self.logger.exception(e)
            abort(400, str(e))


@swagger.model
class QuotaModel:

    resource_fields = {
        'quota': fields.Integer
    }


class Quota(Resource):
    """Quota API"""

    @swagger.operation(
        notes='''Fetch the current Cinder volume quota.  This value limits
        the number of volumes that can be created, and by extension, defines
        the maximum number of agents that can be created for any given test
        scenario''',
        type=QuotaModel.__name__
    )
    def get(self):
        quota = storperf.volume_quota
        return jsonify({'quota': quota})


def setup_logging(default_path='logging.json',
                  default_level=logging.INFO, env_key='LOG_CFG'):
    """Setup logging configuration
    """

    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)

    socketHandler = logging.handlers.DatagramHandler(
        'localhost', logging.handlers.DEFAULT_UDP_LOGGING_PORT)
    rootLogger = logging.getLogger('')
    rootLogger.addHandler(socketHandler)


api.add_resource(Configure, "/api/v1.0/configurations")
api.add_resource(Initialize, "/api/v1.0/initializations")
api.add_resource(Quota, "/api/v1.0/quotas")
api.add_resource(Job, "/api/v1.0/jobs")
api.add_resource(Job_v2, "/api/v2.0/jobs")
api.add_resource(Logs, "/api/v1.0/logs")

if __name__ == "__main__":
    setup_logging()
    logging.getLogger("storperf").setLevel(logging.DEBUG)

    app.run(host='0.0.0.0', debug=True, threaded=True)
