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

virtualenv $WORKSPACE/ci/job/storperf_daily_venv
source $WORKSPACE/ci/job/storperf_daily_venv/bin/activate

pip install --upgrade setuptools
pip install functools32
pip install pytz
pip install osc_lib
pip install python-openstackclient
pip install python-heatclient

# This is set by Jenkins, but if we are running manually, just use the
# current hostname.
if [ -z "$NODE_NAME" ]
then
    NODE_NAME=`hostname`
fi
export POD_NAME=$NODE_NAME

sudo find $WORKSPACE/ -name '*.db' -exec rm -fv {} \;

export INSTALLER=`$WORKSPACE/ci/detect_installer.sh`

$WORKSPACE/ci/generate-admin-rc.sh
$WORKSPACE/ci/generate-environment.sh

. $WORKSPACE/ci/job/environment.rc
for env in `cat $WORKSPACE/ci/job/admin.rc`
do
    export $env
done

echo "Checking for an existing stack"
STACK_ID=`openstack stack list | grep StorPerfAgentGroup | awk '{print $2}'`
if [ ! -z $STACK_ID ]
then
    openstack stack delete --yes --wait StorPerfAgentGroup
fi

echo Checking for Ubuntu 14.04 image in Glance
IMAGE=`openstack image list | grep "Trusty x86_64"`
if [ -z $IMAGE ]
then
    wget https://cloud-images.ubuntu.com/releases/14.04/release/ubuntu-14.04-server-cloudimg-amd64-disk1.img
    openstack image create "Trusty x86_64" --disk-format qcow2 --public \
    --container-format bare --file ubuntu-14.04-server-cloudimg-amd64-disk1.img
fi

echo "TEST_DB_URL=http://testresults.opnfv.org/test/api/v1" >> $WORKSPACE/ci/job/admin.rc
echo "INSTALLER_TYPE=${INSTALLER}" >> $WORKSPACE/ci/job/admin.rc
$WORKSPACE/ci/launch_docker_container.sh

echo "Waiting for StorPerf to become active"
while [ $(curl -X GET 'http://127.0.0.1:5000/api/v1.0/configurations' > /dev/null 2>&1;echo $?) -ne 0 ]
do
    sleep 1
done

echo Creating 1:1 stack
$WORKSPACE/ci/create_stack.sh $CINDER_NODES 10 "Trusty x86_64" $NETWORK

export QUEUE_DEPTH=8
export BLOCK_SIZE=16384
export WORKLOAD=_warm_up
export SCENARIO_NAME="${CINDER_BACKEND}_${WORKLOAD}"
WARM_UP=`$WORKSPACE/ci/start_job.sh | awk '/job_id/ {print $2}' | sed 's/"//g'`

WARM_UP_STATUS=`curl -s -X GET "http://127.0.0.1:5000/api/v1.0/jobs?id=$WARM_UP&type=status" \
    | awk '/Status/ {print $2}' | sed 's/"//g'`
while [ "$WARM_UP_STATUS" != "Completed" ]
do
    sleep 10
    WARM_UP_STATUS=`curl -s -X GET "http://127.0.0.1:5000/api/v1.0/jobs?id=$WARM_UP&type=status" \
    | awk '/Status/ {print $2}' | sed 's/"//g'`
done

for WORKLOAD in ws wr rs rr rw
do
    for BLOCK_SIZE in 2048 8192 16384
    do
        for QUEUE_DEPTH in 1 2 8
        do
            export QUEUE_DEPTH
            export BLOCK_SIZE
            export WORKLOAD
            export SCENARIO_NAME="${CINDER_BACKEND}_${WORKLOAD}"

            JOB=`$WORKSPACE/ci/start_job.sh \
                | awk '/job_id/ {print $2}' | sed 's/"//g'`
            JOB_STATUS=`curl -s -X GET "http://127.0.0.1:5000/api/v1.0/jobs?id=$JOB&type=status" \
                | awk '/Status/ {print $2}' | sed 's/"//g'`
            while [ "$JOB_STATUS" != "Completed" ]
            do
                sleep 10
                JOB_STATUS=`curl -s -X GET "http://127.0.0.1:5000/api/v1.0/jobs?id=$JOB&type=status" \
                    | awk '/Status/ {print $2}' | sed 's/"//g'`
            done
        done
    done
done


echo "Deleting stack for cleanup"
curl -X DELETE --header 'Accept: application/json' 'http://127.0.0.1:5000/api/v1.0/configurations'

exit 0
