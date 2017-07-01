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

cd ${ci}/../docker-compose

export TAG=${DOCKER_TAG:-latest}
export ENV_FILE=${ci}/job/admin.rc
export CARBON_DIR=${ci}/job/carbon/

if [ ! -d ${ci}/job/carbon ]
then
    mkdir ${ci}/job/carbon
    sudo chown 33:33 ${ci}/job/carbon
fi

docker-compose pull
docker-compose up -d

echo "Waiting for StorPerf to become active"
curl -X GET 'http://127.0.0.1:5000/api/v1.0/configurations' > test.html 2>&1
while [ `grep 'agent_count' test.html | wc -l` == "0" ]
do
    sleep 1
    curl -X GET 'http://127.0.0.1:5000/api/v1.0/configurations' > test.html 2>&1
done

rm -f test.html
