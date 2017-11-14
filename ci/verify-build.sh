#!/bin/bash -xe
##############################################################################
# Copyright (c) 2017 Dell EMC and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

cd `dirname $0`
ci=`pwd`

cd ${ci}/../docker

export ENV_FILE=${ci}/job/admin.rc
export CARBON_DIR=${ci}/job/carbon/

${ci}/remove_docker_container.sh

mkdir -p ${CARBON_DIR}
touch ${ENV_FILE}

if [ -z $ARCH ]
then
    ARCH=$(uname -m)
fi

export ARCH=${ARCH}

echo Using $ARCH architecture

docker-compose -f local-docker-compose.yaml down
docker-compose -f local-docker-compose.yaml build
docker-compose -f local-docker-compose.yaml up -d

function check_for_life() {
    NAME=$1
    URI=$2

    echo "Waiting for ${NAME} to become active"
    ATTEMPTS=10

    while [ $(curl -s -o /dev/null -I -w "%{http_code}" -X GET http://127.0.0.1:5000${URI}) != "200" ]
    do
        ATTEMPTS=$((ATTEMPTS - 1))
        if [ ${ATTEMPTS} -le 1 ]
        then
            echo "Failed to get a start up of ${NAME}"
            return 1
        fi
        sleep 2
    done
}

FAILURES=0

set +e

check_for_life storperf-httpfrontend "/"
FAILURES=$((FAILURES + $?))

check_for_life storperf-master "/api/v1.0/jobs"
FAILURES=$((FAILURES + $?))

check_for_life storperf-reporting "/reporting/"
FAILURES=$((FAILURES + $?))

check_for_life storperf-swagger "/swagger/?url=http://127.0.0.1:5000/api/spec.json"
FAILURES=$((FAILURES + $?))

check_for_life storperf-graphite "/graphite/"
FAILURES=$((FAILURES + $?))


for container in master graphite httpfrontend swaggerui reporting
do
    echo "====================================="
    echo "Log for storperf-${container}"
    docker logs storperf-${container}
done
echo "====================================="

docker-compose -f local-docker-compose.yaml down

exit ${FAILURES}
