#!/bin/bash -x
##############################################################################
# Copyright (c) 2015 EMC and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

which juju 2>/dev/null
if [ $? -eq 0 ]
then
    INSTALLER=joid
fi
sudo virsh list --all | grep undercloud >/dev/null
if [ $? -eq 0 ]
then
    INSTALLER=apex
fi

echo $INSTALLER