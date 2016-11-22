##############################################################################
# Copyright (c) 2015 EMC and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

import io
import json
import logging
import logging.config
import os

from flask import abort, Flask, request, jsonify, send_from_directory
from flask_restful import Resource, Api, fields
from flask_restful_swagger import swagger

from storperf.db.job_db import JobDB
from storperf.plot.barchart import Barchart
from storperf.storperf_master import StorPerfMaster


app = Flask(__name__, static_url_path="")
api = swagger.docs(Api(app), apiVersion='1.0')

storperf = StorPerfMaster()


@app.route('/swagger/<path:path>')
def send_swagger(path):
    return send_from_directory('storperf/resources/html/swagger', path)


@app.route('/results/<path:job_id>')
def results_page(job_id):

    job_db = JobDB()
    params = {}

    params = job_db.fetch_workload_params(job_id)

    results = storperf.fetch_results(job_id)
    workloads = []
    block_sizes = []
    queue_depths = []

    for key, value in results.iteritems():
        workload = key.split('.')[0]
        queue_depth = int(key.split('.')[2])
        block_size = int(key.split('.')[4])
        if workload not in workloads:
            workloads.append(workload)
        if queue_depth not in queue_depths:
            queue_depths.append(queue_depth)
        if block_size not in block_sizes:
            block_sizes.append(block_size)

    queue_depths.sort()
    block_sizes.sort()

    read_latencies = []
    write_latencies = []
#    for workload in workloads:
    workload = "rw"

    for queue_depth in queue_depths:
        rlatencies = []
        read_latencies.append(rlatencies)
        wlatencies = []
        write_latencies.append(wlatencies)
        for block_size in block_sizes:

            key = "%s.queue-depth.%s.block-size.%s.read.latency" % \
                (workload, queue_depth, block_size)
            if key in results:
                rlatencies.append(results[key] / 1000)
            else:
                rlatencies.append(0)

            key = "%s.queue-depth.%s.block-size.%s.write.latency" % \
                (workload, queue_depth, block_size)
            if key in results:
                wlatencies.append(results[key] / 1000)
            else:
                wlatencies.append(0)

    chart = Barchart()
    chart.barchart3d(queue_depths, block_sizes, read_latencies, 'g',
                     'Read Latency (ms)')
    readchart = chart.to_base64_image()

    chart.barchart3d(queue_depths, block_sizes, write_latencies, 'r',
                     'Write Latency (ms)')
    writechart = chart.to_base64_image()

    metadata = "<table>"
    for key, value in params.iteritems():
        metadata += "<TR><TD>" + key + "<TD>" + value + "</TR>"
    metadata += "</table>"

    html = """<html><body>%s <BR>
    Number of VMs: %s <BR>
    Cinder volume size per VM: %s (GB) <BR>
    Metadata: <BR>
    %s<BR>
    <center>Read Latency Report <BR>
    <img src="data:image/png;base64,%s"/>
    <center>Write Latency Report <BR>
    <img src="data:image/png;base64,%s"/>
    </body></html>""" % (job_id,
                         params['agent_count'],
                         params['volume_size'],
                         metadata,
                         readchart,
                         writechart,
                         )

    return html


@swagger.model
class ConfigurationRequestModel:
    resource_fields = {
        'agent_count': fields.Integer,
        'agent_image': fields.String,
        'public_network': fields.String,
        'volume_size': fields.Integer
    }


@swagger.model
class ConfigurationResponseModel:
    resource_fields = {
        'agent_count': fields.Integer,
        'agent_image': fields.String,
        'public_network': fields.String,
        'stack_created': fields.Boolean,
        'stack_id': fields.String,
        'volume_size': fields.Integer
    }


class Configure(Resource):

    """Configuration API"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    @swagger.operation(
        notes='Fetch the current agent configuration',
        type=ConfigurationResponseModel.__name__
    )
    def get(self):
        return jsonify({'agent_count': storperf.agent_count,
                        'agent_image': storperf.agent_image,
                        'public_network': storperf.public_network,
                        'volume_size': storperf.volume_size,
                        'stack_created': storperf.is_stack_created,
                        'stack_id': storperf.stack_id})

    @swagger.operation(
        notes='''Set the current agent configuration and create a stack in
        the controller.  Returns once the stack request is submitted.''',
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
            if ('agent_count' in request.json):
                storperf.agent_count = request.json['agent_count']
            if ('agent_image' in request.json):
                storperf.agent_image = request.json['agent_image']
            if ('public_network' in request.json):
                storperf.public_network = request.json['public_network']
            if ('volume_size' in request.json):
                storperf.volume_size = request.json['volume_size']

            storperf.create_stack()

            return jsonify({'agent_count': storperf.agent_count,
                            'agent_image': storperf.agent_image,
                            'public_network': storperf.public_network,
                            'volume_size': storperf.volume_size,
                            'stack_id': storperf.stack_id})

        except Exception as e:
            abort(400, str(e))

    @swagger.operation(
        notes='Deletes the agent configuration and the stack'
    )
    def delete(self):
        try:
            storperf.delete_stack()
        except Exception as e:
            abort(400, str(e))


@swagger.model
class WorkloadModel:
    resource_fields = {
        'target': fields.String,
        'nossd': fields.String,
        'nowarm': fields.String,
        'deadline': fields.Integer,
        'workload': fields.String,
        'queue_depths': fields.String,
        'block_sizes': fields.String
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
                "required": True,
                "type": "string",
                "allowMultiple": False,
                "paramType": "query"
            },
            {
                "name": "type",
                "description": "The type of metrics to report.  May be "
                "metrics (default), or metadata",
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

        type = "metrics"
        if request.args.get('type'):
            type = request.args.get('type')

        workload_id = request.args.get('id')

        if type == "metrics":
            return jsonify(storperf.fetch_results(workload_id))

        if type == "metadata":
            return jsonify(storperf.fetch_metadata(workload_id))

        if type == "status":
            return jsonify({"Status": storperf.fetch_job_status(workload_id)})

    @swagger.operation(
        parameters=[
            {
                "name": "body",
                "description": """Start execution of a workload with the
following parameters:

"target": The target device to profile",

"deadline": if specified, the maximum duration in minutes
for any single test iteration.

"nossd": Do not fill the target with random
data prior to running the test,

"nowarm": Do not refill the target with data
prior to running any further tests,

"workload":if specified, the workload to run. Defaults to all.
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

        self.logger.info(request.json)

        try:
            if ('target' in request.json):
                storperf.filename = request.json['target']
            if ('deadline' in request.json):
                storperf.deadline = request.json['deadline']
            if ('nossd' in request.json):
                storperf.precondition = False
            if ('nowarm' in request.json):
                storperf.warm_up = False
            if ('queue_depths' in request.json):
                storperf.queue_depths = request.json['queue_depths']
            if ('block_sizes' in request.json):
                storperf.block_sizes = request.json['block_sizes']
            if ('workload' in request.json):
                storperf.workloads = request.json['workload']
            else:
                storperf.workloads = None
            if ('metadata' in request.json):
                metadata = request.json['metadata']
            else:
                metadata = {}

            job_id = storperf.execute_workloads(metadata)

            return jsonify({'job_id': job_id})

        except Exception as e:
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
        try:
            return jsonify({'Slaves': storperf.terminate_workloads()})
        except Exception as e:
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


def setup_logging(default_path='storperf/logging.json',
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
api.add_resource(Quota, "/api/v1.0/quotas")
api.add_resource(Job, "/api/v1.0/jobs")

if __name__ == "__main__":
    setup_logging()
    logging.getLogger("storperf").setLevel(logging.DEBUG)

    app.run(host='0.0.0.0', debug=True)
