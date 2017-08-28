#!/bin/bash
##############################################################################
# Copyright (c) 2017 EMC and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

echo "Checking for Ubuntu 16.04 image in Glance"
IMAGE=`openstack image list | grep "Ubuntu 16.04 x86_64"`
if [ -z "$IMAGE" ]
then
    wget -q https://cloud-images.ubuntu.com/releases/16.04/release/ubuntu-16.04-server-cloudimg-amd64-disk1.img
    openstack image create "Ubuntu 16.04 x86_64" --disk-format qcow2 --public \
    --container-format bare --file ubuntu-16.04-server-cloudimg-amd64-disk1.img
fi

openstack image show "Ubuntu 16.04 x86_64"

exit 0
