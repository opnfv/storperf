#!/bin/bash
##############################################################################
# Copyright (c) 2016 EMC and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

cd $(dirname "$0")

if [ ! -d job ]
then
    mkdir job
fi

SSH_KEY=""
INSTALLER="$(./detect_installer.sh)"
case $INSTALLER in
    joid)
        OS_AUTH_URL=http://`juju status keystone | grep public | awk '{print $2}'`:5000/v2.0
        OS_USERNAME=admin
        OS_PASSWORD=openstack
        cat << EOF > job/openstack.rc
export OS_AUTH_URL=$OS_AUTH_URL
export OS_USERNAME=$OS_USERNAME
export OS_PASSWORD=$OS_PASSWORD
export OS_TENANT_NAME=admin
export OS_PROJECT_NAME=admin
EOF
        ;;
    fuel)
        INSTALLER_IP=$(sudo virsh domifaddr cfg01 | grep ipv4 | awk '{print $4}' | cut -d/ -f1)
        export BRANCH="${BRANCH:-master}"
        SALT_MASTER=${INSTALLER_IP}
        SSH_KEY="-s /var/lib/opnfv/mcp.rsa"
        ;;
    apex)
        INSTALLER_IP=$(sudo virsh domifaddr undercloud | grep ipv4 | awk '{print $4}' | cut -d/ -f1)
        ;;
    *)
        echo "Unknown installer ${INSTALLER}"
        exit 1
esac

if [ ! -z "${INSTALLER_IP}" ]
then
    CMD="./job/releng/utils/fetch_os_creds.sh -i $INSTALLER -a $INSTALLER_IP $SSH_KEY -d job/openstack.rc"
    echo $CMD
    $CMD

    echo export OS_PROJECT_NAME=admin >> job/openstack.rc
fi

grep "export" job/openstack.rc | sed "s/export //"  > job/admin.rc
echo "INSTALLER_TYPE=${INSTALLER}" >> job/admin.rc
