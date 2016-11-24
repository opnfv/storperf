#!/bin/bash
##############################################################################
# Copyright (c) 2016 EMC and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

cd `dirname $0`

storperf_container=`docker ps -a -q -f name=storperf`

if [ ! -z $storperf_container ]
then
    echo "Stopping any existing StorPerf container"
    docker rm -fv $storperf_container
fi

if [ ! -f job/admin.rc ]
then
    ./generate-admin-rc.sh
fi

if [ ! -d job/carbon ]
then
    mkdir job/carbon
    sudo chown 33:33 job/carbon
fi

docker run -d --env-file `pwd`/job/admin.rc \
    -p 5000:5000 \
    -p 8000:8000 \
    -v `pwd`/job/carbon:/opt/graphite/storage/whisper \
    -v `pwd`/../../storperf:/home/opnfv/repos/storperf \
    --name storperf opnfv/storperf


