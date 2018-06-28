#!/bin/bash
##############################################################################
# Copyright (c) 2017 EMC and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

echo "Checking for StorPerf flavor"

FLAVOUR=`openstack flavor list | grep "storperf"`
if [ -z "$FLAVOUR" ]
then
    openstack flavor create storperf \
        --id auto \
        --ram 8192 \
        --disk 4 \
        --vcpus 2
fi

openstack flavor show storperf
