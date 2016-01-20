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

from flask import abort, Flask, request, jsonify
from flask_restful import Resource, Api


app = Flask(__name__)
api = Api(app)
storperf = StorPerfMaster()


class Configure(Resource):

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get(self):
        return jsonify({'agent_count': storperf.agent_count,
                        'agent_network': storperf.agent_network,
                        'volume_size': storperf.volume_size,
                        'stack_created': storperf.is_stack_created,
                        'stack_id': storperf.stack_id})

    def post(self):
        if not request.json:
            abort(400, "ERROR: No data specified")

        try:
            if ('agent_count' in request.json):
                storperf.agent_count = request.json['agent_count']
            if ('agent_network' in request.json):
                storperf.agent_network = request.json['agent_network']
            if ('volume_size' in request.json):
                storperf.volume_size = request.json['volume_size']

            storperf.validate_stack()
            storperf.create_stack()

            return jsonify({'agent_count': storperf.agent_count,
                            'agent_network': storperf.agent_network,
                            'volume_size': storperf.volume_size,
                            'stack_id': storperf.stack_id})

        except Exception as e:
            abort(400, str(e))

    def delete(self):
        try:
            storperf.delete_stack()
        except Exception as e:
            print e
            abort(400, str(e))
        pass


class StartJob(Resource):

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def post(self):
        if not request.json:
            abort(400, "ERROR: Missing configuration data")

        self.logger.info(request.json)

        try:
            if ('target' in request.json):
                storperf.filename = request.json['filename']
            if ('nossd' in request.json):
                storperf.precondition = False
            if ('nowarm' in request.json):
                storperf.warm_up = False
            if ('workload' in request.json):
                storperf.workloads = request.json['workload']

            job_id = storperf.execute_workloads()

            return jsonify({'job_id': job_id})

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
api.add_resource(StartJob, "/api/v1.0/start")

if __name__ == "__main__":
    setup_logging()
    logging.getLogger("storperf").setLevel(logging.DEBUG)

    app.run(host='0.0.0.0', debug=True)
