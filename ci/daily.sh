#!/bin/bash -x
##############################################################################
# Copyright (c) 2015 EMC and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

if [ -z $WORKSPACE ]
then
    cd `dirname $0`/..
    WORKSPACE=`pwd`
fi

if [ -d $WORKSPACE/ci/job ]
then
    sudo rm -rf $WORKSPACE/ci/job
fi
sudo find $WORKSPACE/ -name '*.db' -exec rm -fv {} \;

$WORKSPACE/ci/generate-admin-rc.sh
$WORKSPACE/ci/generate-environment.sh

. $WORKSPACE/ci/job/environment.rc
for env in `cat $WORKSPACE/ci/job/admin.rc`
do
    export $env
done

echo "Checking for an existing stack"
STACK_ID=`heat stack-list | grep StorPerfAgentGroup | awk '{print $2}'`
if [ ! -z $STACK_ID ]
then
    heat stack-delete -y StorPerfAgentGroup
fi

while [ ! -z $STACK_ID ]
do
    STACK_ID=`heat stack-list | grep StorPerfAgentGroup | awk '{print $2}'`
done

echo "TEST_DB_URL=http://testresults.opnfv.org/test/api/v1" >> $WORKSPACE/ci/job/admin.rc
$WORKSPACE/ci/launch_docker_container.sh

echo "Waiting for StorPerf to become active"
while [ $(curl -X GET 'http://127.0.0.1:5000/api/v1.0/configurations' > /dev/null 2>&1;echo $?) -ne 0 ]
do
    sleep 1
done

echo Creating 1:1 stack
$WORKSPACE/ci/create_stack.sh $CINDER_NODES 1
WARM_UP=`$WORKSPACE/ci/warmup.sh "${CINDER_BACKEND}" ${CINDER_NODES} | grep job_id | awk '{print $2}' | sed 's/"//g'`

WARM_UP_STATUS=`curl -s -X GET "http://127.0.0.1:5000/api/v1.0/jobs?id=$WARM_UP&type=status" \
    | grep Status | awk '{print $2}' | sed 's/"//g'`
while [ "$WARM_UP_STATUS" != "Completed" ]
do
    sleep 10
    WARM_UP_STATUS=`curl -s -X GET "http://127.0.0.1:5000/api/v1.0/jobs?id=$WARM_UP&type=status" \
    | grep Status | awk '{print $2}' | sed 's/"//g'`
done


for WORKLOAD in ws wr rs rr rw
do
    for BLOCK_SIZE in 2048 8192 16384
    do
        for QUEUE_DEPTH in 1 2 8
        do
            JOB=`$WORKSPACE/ci/start_job.sh $BLOCK_SIZE $QUEUE_DEPTH ${WORKLOAD} "${CINDER_BACKEND}_${WORKLOAD}" ${CINDER_NODES} \
                | grep job_id | awk '{print $2}' | sed 's/"//g'`
        
            JOB_STATUS=`curl -s -X GET "http://127.0.0.1:5000/api/v1.0/jobs?id=$JOB&type=status" \
                | grep Status | awk '{print $2}' | sed 's/"//g'`
            while [ "$JOB_STATUS" != "Completed" ]
            do
                sleep 10
                JOB_STATUS=`curl -s -X GET "http://127.0.0.1:5000/api/v1.0/jobs?id=$JOB&type=status" \
                    | grep Status | awk '{print $2}' | sed 's/"//g'`
            done
        done
    done
done


echo "Deleting stack for cleanup"
curl -X DELETE --header 'Accept: application/json' 'http://127.0.0.1:5000/api/v1.0/configurations'

exit 0
