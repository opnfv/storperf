#!/bin/bash -x
##############################################################################
# Copyright (c) 2016 EMC and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

cd `dirname $0`
ci=`pwd`

cd ${ci}/../docker

export TAG=${DOCKER_TAG:-latest}
export ENV_FILE=${ci}/job/admin.rc
export CARBON_DIR=${ci}/job/carbon/

docker-compose -f local-docker-compose.yaml down

for container_name in storperf storperf-master storperf-swaggerui storperf-httpfrontend storperf-reporting storperf-graphite
do
    container=`docker ps -a -q -f name=$container_name`
    if [ ! -z $container ]
    then
        echo "Stopping any existing $container_name container"
        docker rm -fv $container
    fi
done
