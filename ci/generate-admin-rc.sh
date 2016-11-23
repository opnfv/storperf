#!/bin/bash
##############################################################################
# Copyright (c) 2016 EMC and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

cd `dirname $0`

# TODO: Switch based on installer type, for now this is hard coded to JOID only

if [ ! -d job ]
then
	mkdir job
fi

export OS_AUTH_URL=http://`juju status keystone | grep public | awk '{print $2}'`:5000/v2.0
export OS_USERNAME=admin
export OS_PASSWORD=openstack

export OS_TENANT_ID=`keystone tenant-list 2>/dev/null | grep "admin" | awk '{print $2}'`

cat << EOF > job/admin.rc
OS_AUTH_URL=$OS_AUTH_URL
OS_USERNAME=$OS_USERNAME
OS_PASSWORD=$OS_PASSWORD
OS_TENANT_ID=$OS_TENANT_ID
OS_TENANT_NAME=admin
OS_PROJECT_NAME=admin
OS_REGION_NAME=RegionOne
EOF

