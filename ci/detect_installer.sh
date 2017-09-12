#!/bin/bash -x
##############################################################################
# Copyright (c) 2015 EMC and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

if which juju >/dev/null 2>&1 ; then
    INSTALLER=joid
fi

if sudo virsh list --all | grep -q undercloud ; then
    INSTALLER=apex
fi

if sudo virsh list --all | grep -q cfg01 ; then
    INSTALLER=fuel
fi

echo $INSTALLER
