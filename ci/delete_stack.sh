#!/bin/bash
##############################################################################
# Copyright (c) 2017 EMC and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

echo "Checking for an existing stack"
STACK_ID=`openstack stack list | grep StorPerfAgentGroup | awk '{print $2}'`
if [ ! -z $STACK_ID ]
then
    openstack stack delete --yes --wait StorPerfAgentGroup
fi
