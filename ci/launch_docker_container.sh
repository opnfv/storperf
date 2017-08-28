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

export ENV_FILE=${ci}/job/admin.rc
export CARBON_DIR=${ci}/job/carbon/

if [ ! -d ${ci}/job/carbon ]
then
    mkdir ${ci}/job/carbon
    sudo chown 33:33 ${ci}/job/carbon
fi

if [ -z $ARCH ]
then
    ARCH=x86_64
fi

export ARCH

docker-compose -f local-docker-compose.yaml build
docker-compose -f local-docker-compose.yaml up -d

echo "Waiting for StorPerf to become active"

ATTEMPTS=20

while [ $(curl -s -o /dev/null -I -w "%{http_code}" -X GET http://127.0.0.1:5000/api/v1.0/configurations) != "200" ]
do
    ATTEMPTS=$((ATTEMPTS - 1))
    if [ ${ATTEMPTS} -le 1 ]
    then
        echo "Failed to get a start up of StorPerf Master"
        exit 1
    fi
    sleep 1
done
