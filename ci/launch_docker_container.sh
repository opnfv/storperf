#!/bin/bash -x
##############################################################################
# Copyright (c) 2016 EMC and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

cd "$(dirname "$0")" || exit 1
ci=$(pwd)

cd "${ci}/../docker-compose" || exit 1

export ENV_FILE="${ci}/job/admin.rc"
export CARBON_DIR="${ci}/job/carbon/"

if [ ! -d "${ci}/job/carbon" ]
then
    mkdir -p "${ci}/job/carbon"
fi

ARCH="${ARCH:-$(uname -m)}"
export ARCH

DOCKER_TAG="${DOCKER_TAG:-latest}"

export TAG="${ARCH}-${DOCKER_TAG}"

docker-compose pull
docker-compose up -d

echo "Waiting for StorPerf to become active"

ATTEMPTS=20

while [ "$(curl -s -o /dev/null -I -w '%{http_code}' -X GET http://127.0.0.1:5000/api/v1.0/configurations)" != "200" ]
do
    ATTEMPTS=$((ATTEMPTS - 1))
    if [ ${ATTEMPTS} -le 1 ]
    then
        echo "Failed to get a start up of StorPerf Master"
        exit 1
    fi
    sleep 1
done
