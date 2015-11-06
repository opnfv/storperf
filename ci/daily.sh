#!/bin/bash -x
##############################################################################
# Copyright (c) 2015 EMC and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

if [ -f ~/jenkins-os.rc ]
then
    . ~/jenkins-os.rc
fi

if [ -z $WORKSPACE ]
then
    WORKSPACE=`pwd`
fi

function stage_base_os_in_glance {

   export OS_IMAGE_API_VERSION=1

    glance image-list | grep "$1"
    if [ $? -eq 1 ]
    then
        curl -s -o $WORKSPACE/$1.qcow2 https://cloud-images.ubuntu.com/releases/15.10/release/ubuntu-15.10-server-cloudimg-amd64-disk1.img
        glance image-create --name="$1" --disk-format=qcow2 --container-format=bare < $WORKSPACE/$1.qcow2
    fi

}

stage_base_os_in_glance ubuntu-server

exit 0
