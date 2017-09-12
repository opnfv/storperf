#!/bin/bash -xe
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

docker-compose --version
if [ $? -ne 0 ]
then
    echo "Docker compose is missing"
    exit 1
fi

git clone --depth 1 https://gerrit.opnfv.org/gerrit/releng $WORKSPACE/ci/job/releng

virtualenv $WORKSPACE/ci/job/storperf_daily_venv
source $WORKSPACE/ci/job/storperf_daily_venv/bin/activate

pip install --upgrade setuptools==33.1.1
pip install functools32==3.2.3.post2
pip install pytz==2016.10
pip install osc_lib==1.3.0
pip install python-openstackclient==3.7.0
pip install python-heatclient==1.7.0

$WORKSPACE/ci/generate-admin-rc.sh
echo "TEST_DB_URL=http://testresults.opnfv.org/test/api/v1" >> $WORKSPACE/ci/job/admin.rc
$WORKSPACE/ci/generate-environment.sh

. $WORKSPACE/ci/job/environment.rc

while read -r env
do
    export "$env"
done < $WORKSPACE/ci/job/admin.rc

export AGENT_COUNT=${AGENT_COUNT:-$CINDER_NODES}
export BLOCK_SIZES=${BLOCK_SIZES:-1024,16384}
export STEADY_STATE_SAMPLES=${STEADY_STATE_SAMPLES:-10}
export DEADLINE=${DEADLINE:-`expr $STEADY_STATE_SAMPLES \* 3`}
export DISK_TYPE=${DISK_TYPE:-unspecified}
export QUEUE_DEPTHS=${QUEUE_DEPTHS:-1,4}
export POD_NAME=${NODE_NAME:-`hostname`}
export SCENARIO_NAME=${DEPLOY_SCENARIO:-none}
export TEST_CASE=${TEST_CASE:-snia_steady_state}
export VERSION=`echo ${BUILD_TAG#*daily-} | cut -d- -f1`
export VOLUME_SIZE=${VOLUME_SIZE:-2}
export WORKLOADS=${WORKLOADS:-ws,wr,rs,rr,rw}

echo ==========================================================================
echo Environment
env | sort
echo ==========================================================================

$WORKSPACE/ci/remove_docker_container.sh
$WORKSPACE/ci/delete_stack.sh
$WORKSPACE/ci/create_glance_image.sh
$WORKSPACE/ci/create_storperf_flavor.sh
$WORKSPACE/ci/launch_docker_container.sh
$WORKSPACE/ci/create_stack.sh $AGENT_COUNT $VOLUME_SIZE "Ubuntu 16.04 x86_64" $NETWORK

export WORKLOAD=_warm_up,$WORKLOADS
export BLOCK_SIZE=$BLOCK_SIZES
export QUEUE_DEPTH=$QUEUE_DEPTHS

echo ==========================================================================
echo Starting run of $WORKLOAD $BLOCK_SIZE $QUEUE_DEPTH
echo ==========================================================================

JOB=`$WORKSPACE/ci/start_job.sh \
    | awk '/job_id/ {print $2}' | sed 's/"//g'`
curl -s -X GET "http://127.0.0.1:5000/api/v1.0/jobs?id=$JOB&type=status" \
    -o $WORKSPACE/ci/job/status.json

JOB_STATUS=`cat $WORKSPACE/ci/job/status.json | awk '/Status/ {print $2}' | cut -d\" -f2`
while [ "$JOB_STATUS" != "Completed" ]
do
    sleep 600
    mv $WORKSPACE/ci/job/status.json $WORKSPACE/ci/job/old-status.json
    curl -s -X GET "http://127.0.0.1:5000/api/v1.0/jobs?id=$JOB&type=status" \
        -o $WORKSPACE/ci/job/status.json
    JOB_STATUS=`cat $WORKSPACE/ci/job/status.json | awk '/Status/ {print $2}' | cut -d\" -f2`
    if diff $WORKSPACE/ci/job/status.json $WORKSPACE/ci/job/old-status.json >/dev/null
    then
        cat $WORKSPACE/ci/job/status.json
    fi
done

set +e

echo "Deleting stack for cleanup"
curl -s -X DELETE --header 'Accept: application/json' 'http://127.0.0.1:5000/api/v1.0/configurations'

curl -s -X GET "http://127.0.0.1:5000/api/v1.0/jobs?id=$JOB&type=metadata" \
    -o $WORKSPACE/ci/job/report.json

$WORKSPACE/ci/remove_docker_container.sh

sudo rm -rf $WORKSPACE/ci/job/carbon
sudo find $WORKSPACE/docker --name '*.db' -exec rm -fv {} \;

echo ==========================================================================
echo Final report
echo ==========================================================================
cat $WORKSPACE/ci/job/report.json

exit 0
