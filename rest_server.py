##############################################################################
# Copyright (c) 2015 EMC and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

from storperf.storperf_master import StorPerfMaster
import json
import logging
import logging.config
import os

from flask import abort, Flask, request, jsonify, send_from_directory
from flask_restful import Resource, Api, fields
from flask_restful_swagger import swagger

app = Flask(__name__, static_url_path="")
api = swagger.docs(Api(app), apiVersion='1.0')

storperf = StorPerfMaster()


@app.route('/swagger/<path:path>')
def send_swagger(path):
    print "called! storperf/resources/html/swagger/" + path
    return send_from_directory('storperf/resources/html/swagger', path)


class Configure(Resource):

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get(self):
        return jsonify({'agent_count': storperf.agent_count,
                        'public_network': storperf.public_network,
                        'volume_size': storperf.volume_size,
                        'stack_created': storperf.is_stack_created,
                        'stack_id': storperf.stack_id})

    def post(self):
        if not request.json:
            abort(400, "ERROR: No data specified")

        try:
            if ('agent_count' in request.json):
                storperf.agent_count = request.json['agent_count']
            if ('public_network' in request.json):
                storperf.public_network = request.json['public_network']
            if ('volume_size' in request.json):
                storperf.volume_size = request.json['volume_size']

            storperf.validate_stack()
            storperf.create_stack()

            return jsonify({'agent_count': storperf.agent_count,
                            'public_network': storperf.public_network,
                            'volume_size': storperf.volume_size,
                            'stack_id': storperf.stack_id})

        except Exception as e:
            abort(400, str(e))

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
        'workload': fields.String,
    }


class Job(Resource):

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    @swagger.operation(
        notes='Fetch the average latency of the specified workload',
        parameters=[
            {
                "name": "id",
                "description": "The UUID of the workload in the format "
                "NNNNNNNN-NNNN-NNNN-NNNN-NNNNNNNNNNNN",
                "required": True,
                "type": "string",
                "allowMultiple": False,
                "paramType": "query"
            }
        ],
        responseMessages=[
            {
                "code": 200,
                "message": "Wordload ID found, response in JSON format"
            },
            {
                "code": 404,
                "message": "Workload ID not found"
            }
        ]
    )
    def get(self):
        workload_id = request.args.get('id')
        print workload_id
        return jsonify(storperf.fetch_results(workload_id))

    @swagger.operation(
        parameters=[
            {
                "name": "body",
                "description": 'Start execution of a workload with the '
                'following parameters: "target": The target device to '
                'profile", "nossd": Do not fill the target with random '
                'data prior to running the test, "nowarm": Do not '
                'refill the target with data '
                'prior to running any further tests, "workload":if specified, '
                'the workload to run. Defaults to all.',
                "required": True,
                "type": "WorkloadModel",
                "paramType": "body"
            }
        ],
        responseMessages=[
            {
                "code": 200,
                "message": "Wordload ID found, response in JSON format"
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
            if ('nossd' in request.json):
                storperf.precondition = False
            if ('nowarm' in request.json):
                storperf.warm_up = False
            if ('workload' in request.json):
                storperf.workloads = request.json['workload']
            else:
                storperf.workloads = None
            # Add block size, queue depth, number of passes here.
            if ('workload' in request.json):
                storperf.workloads = request.json['workload']

            job_id = storperf.execute_workloads()

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
            storperf.terminate_workloads()
            return True
        except Exception as e:
            abort(400, str(e))


class Quota(Resource):

    def get(self):
        quota = storperf.get_volume_quota()
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


api.add_resource(Configure, "/api/v1.0/configure")
api.add_resource(Quota, "/api/v1.0/quota")
api.add_resource(Job, "/api/v1.0/job")

if __name__ == "__main__":
    setup_logging()
    logging.getLogger("storperf").setLevel(logging.DEBUG)

    app.run(host='0.0.0.0', debug=True)
