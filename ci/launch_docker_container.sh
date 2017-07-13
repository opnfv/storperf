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

docker-compose -f local-docker-compose.yaml build
docker-compose -f local-docker-compose.yaml up -d

echo "Waiting for StorPerf to become active"

while [ $(curl -s -o /dev/null -I -w "%{http_code}" -X GET http://127.0.0.1:5000/api/v1.0/configurations) != "200" ]
do
    sleep 1
done
