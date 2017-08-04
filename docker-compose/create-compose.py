from builtins import input
import readline
readline.parse_and_bind("tab: complete")

content = '''# Copyright (c) 2017 Dell EMC and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

version: '2'
services:
    storperf-master:
        container_name: "storperf-master"
        image: "opnfv/storperf-master:{storperf_tag}"
        ports:
            - "8000:8000"
        env_file: {ENV_FILE}
        volumes:
            - {CARBON_DIR}:/opt/graphite/storage/whisper

    storperf-reporting:
        container_name: "storperf-reporting"
        image: "opnfv/storperf-reporting:{reporting_tag}"
        ports:
            - "5080:5000"

    storperf-swaggerui:
        container_name: "storperf-swaggerui"
        image: "schickling/swagger-ui"

    storperf-httpfrontend:
        container_name: "storperf-httpfrontend"
        image: "opnfv/storperf-httpfrontend:{frontend_tag}"
        ports:
            - "5000:5000"
        links:
            - storperf-master
            - storperf-reporting
            - storperf-swaggerui

'''
storeperf_tag = input("Enter image TAG for storperf-master: ") or 'latest'
assert isinstance(storeperf_tag, str)

reporting_tag = input("Enter image TAG for reporting: ") or 'latest'
assert isinstance(reporting_tag, str)

frontend_tag = input("Enter image TAG for frontend: ") or 'latest'
assert isinstance(frontend_tag, str)

swaggerui_tag = input("Enter image TAG for swaggerui: ") or 'later'
assert isinstance(swaggerui_tag, str)

env_file = input("Enter path to environment file: ")
assert isinstance(env_file, str)
if env_file == '':
    print("Did not specify environment file")
    exit(0)

carbon_dir = input("Enter path to Carbon: ")
assert isinstance(carbon_dir, str)
if carbon_dir == '':
    print("Did not specify Carbon Directory")
    exit(0)

f = open('docker-compose.yaml', 'w')
f.write(content.format(storperf_tag=storeperf_tag, reporting_tag=reporting_tag,
                       frontend_tag=frontend_tag, swaggerui_tag=swaggerui_tag,
                       CARBON_DIR=carbon_dir, ENV_FILE=env_file))

f.close()
