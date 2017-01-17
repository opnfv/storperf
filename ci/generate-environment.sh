#!/bin/bash -x
##############################################################################
# Copyright (c) 2015 EMC and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

cd `dirname $0`
if [ ! -d job ]
then
    mkdir job
fi
ssh_options="-o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"

export INSTALLER=`./detect_installer.sh`

case $INSTALLER in
    joid)
        # Determine Cinder backend
        if [ ! -z "$(juju status | grep ceph)" ]
        then
            CINDER_BACKEND=ceph
            JUJU_CHARM=ceph-osd
        fi
        if [ ! -z "$(juju status | grep scaleio)" ]
        then
            CINDER_BACKEND=scaleio
            JUJU_CHARM=scaleio-sds
        fi
        # Determine how many storage blades we have
        CINDER_NODES=`juju status | grep "$JUJU_CHARM/" | wc -l`
        # Later, collect info about each node:
        # juju status | grep hardware: | grep tags | grep -v virtual
        NETWORK=ext-net
        ;;
    apex)
        INSTALLER_IP=`sudo virsh domifaddr undercloud | grep ipv4 | awk '{print $4}' | cut -d/ -f1`
        CINDER_BACKEND=ceph
        sudo scp $ssh_options root@$INSTALLER_IP:/home/stack/instackenv.json job/
        CINDER_NODES=`grep capabilities job/instackenv.json | wc -l`
        NETWORK=external
        ;;
    *)
        CINDER_BACKEND=ceph
        CINDER_NODES=4
        NETWORK=external
esac

cat << EOF > job/environment.rc
export CINDER_BACKEND=$CINDER_BACKEND
export CINDER_NODES=$CINDER_NODES
export INSTALLER=$INSTALLER
export NETWORK=$NETWORK
EOF