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

export INSTALLER=`./detect_installer.sh`
case $INSTALLER in
    joid)
        export OS_AUTH_URL=http://`juju status keystone | grep public | awk '{print $2}'`:5000/v2.0
        export OS_USERNAME=admin
        export OS_PASSWORD=openstack
        cat << EOF > job/openstack.rc
export OS_AUTH_URL=$OS_AUTH_URL
export OS_USERNAME=$OS_USERNAME
export OS_PASSWORD=$OS_PASSWORD
export OS_TENANT_NAME=admin
export OS_PROJECT_NAME=admin
EOF
        ;;
    apex)
        INSTALLER_IP=`sudo virsh domifaddr undercloud | grep ipv4 | awk '{print $4}' | cut -d/ -f1`
        ;;
esac

if [ ! -z $INSTALLER_IP ]
then
    ../../releng/utils/fetch_os_creds.sh -i $INSTALLER -a $INSTALLER_IP -d job/openstack.rc
    echo export OS_PROJECT_NAME=admin >> job/openstack.rc
fi

sed "s/export //" job/openstack.rc > job/admin.rc