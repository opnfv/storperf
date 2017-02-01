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

git clone --depth 1 https://gerrit.opnfv.org/gerrit/releng $WORKSPACE/ci/job/releng

virtualenv $WORKSPACE/ci/job/storperf_daily_venv
source $WORKSPACE/ci/job/storperf_daily_venv/bin/activate

pip install --upgrade setuptools==33.1.1
pip install functools32==3.2.3.post2
pip install pytz==2016.10
pip install osc_lib==1.3.0
pip install python-openstackclient==3.7.0
pip install python-heatclient==1.7.0

# This is set by Jenkins, but if we are running manually, just use the
# current hostname.
if [ -z "$NODE_NAME" ]
then
    NODE_NAME=`hostname`
fi
export POD_NAME=$NODE_NAME

# Unless we get a job that automatically deploys Apex or other installers,
# we have to rely on there being a value written into a file to tell us
# what scenario was deployed.  This file needs to tell us:
# DEPLOYED_SCENARIO
# DISK_TYPE
if [ -f ~/jenkins-env.rc ]
then
    . ~/jenkins-env.rc
fi
export SCENARIO_NAME=$DEPLOYED_SCENARIO

sudo find $WORKSPACE/ -name '*.db' -exec rm -fv {} \;

$WORKSPACE/ci/generate-admin-rc.sh
echo "TEST_DB_URL=http://testresults.opnfv.org/test/api/v1" >> $WORKSPACE/ci/job/admin.rc
$WORKSPACE/ci/generate-environment.sh

. $WORKSPACE/ci/job/environment.rc

while read -r env
do
    export "$env"
done < $WORKSPACE/ci/job/admin.rc

export VERSION=`echo ${BUILD_TAG#*daily-} | cut -d- -f1`

echo ==========================================================================
echo Environment
env | sort
echo ==========================================================================

$WORKSPACE/ci/delete_stack.sh
$WORKSPACE/ci/create_glance_image.sh
$WORKSPACE/ci/create_storperf_flavor.sh
$WORKSPACE/ci/launch_docker_container.sh
$WORKSPACE/ci/create_stack.sh $CINDER_NODES 10 "Ubuntu 16.04 x86_64" $NETWORK

echo ==========================================================================
echo Starting warmup
echo ==========================================================================

export QUEUE_DEPTH=8
export BLOCK_SIZE=16384
export WORKLOAD=_warm_up
WARM_UP=`$WORKSPACE/ci/start_job.sh | awk '/job_id/ {print $2}' | sed 's/"//g'`

WARM_UP_STATUS=`curl -s -X GET "http://127.0.0.1:5000/api/v1.0/jobs?id=$WARM_UP&type=status" \
    | awk '/Status/ {print $2}' | cut -d\" -f2`
while [ "$WARM_UP_STATUS" != "Completed" ]
do
    sleep 60
    curl -s -X GET "http://127.0.0.1:5000/api/v1.0/jobs?id=$WARM_UP&type=status"
    WARM_UP_STATUS=`curl -s -X GET "http://127.0.0.1:5000/api/v1.0/jobs?id=$WARM_UP&type=status" \
    | awk '/Status/ {print $2}' | cut -d\" -f2`
done

echo ==========================================================================
echo Starting full matrix run
echo ==========================================================================

export WORKLOAD=ws,wr,rs,rr,rw
export BLOCK_SIZE=2048,8192,16384
export QUEUE_DEPTH=1,2,8
export TEST_CASE=snia_steady_state

JOB=`$WORKSPACE/ci/start_job.sh \
    | awk '/job_id/ {print $2}' | sed 's/"//g'`
JOB_STATUS=`curl -s -X GET "http://127.0.0.1:5000/api/v1.0/jobs?id=$JOB&type=status" \
    | awk '/Status/ {print $2}' | cut -d\" -f2`
while [ "$JOB_STATUS" != "Completed" ]
do
    sleep 60
    curl -s -X GET "http://127.0.0.1:5000/api/v1.0/jobs?id=$JOB&type=status"
    JOB_STATUS=`curl -s -X GET "http://127.0.0.1:5000/api/v1.0/jobs?id=$JOB&type=status" \
    | awk '/Status/ {print $2}' | cut -d\" -f2`
done

HREF=`curl -s -X GET "http://127.0.0.1:5000/api/v1.0/jobs?id=$JOB&type=status" \
    | awk '/TestResultURL/ {print $2}' | cut -d\" -f2 | cut -d/ -f4-`

echo "Deleting stack for cleanup"
curl -X DELETE --header 'Accept: application/json' 'http://127.0.0.1:5000/api/v1.0/configurations'

sudo chmod 777 -R $WORKSPACE/ci/job/carbon

echo "Results published to: http://testresults.opnfv.org/test/$HREF"

exit 0
