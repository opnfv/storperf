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

mkdir -p job

SSH_KEY=""
CA_CERT=""
INSTALLER="$(./detect_installer.sh)"
case $INSTALLER in
    joid)
        CUR_DIR="$(pwd)"
        set -x
        export JOB_DIR="${CUR_DIR}/job"
        sed -i '/echo_info "Creating external network with neutron"/i \
exit 0' job/joid/ci/openstack.sh
        sed -i "s|~/joid_config/admin-openrc|${JOB_DIR}/openstack.rc|g" job/joid/ci/openstack.sh
        cd job/joid/ci
        ./openstack.sh
        cd "${CUR_DIR}"
        ;;
    fuel)
        INSTALLER_IP=$(sudo virsh net-dumpxml mcpcontrol | grep 'cfg01' | cut -d"'" -f6)
        if [ -z "${INSTALLER_IP}" ] ; then
            echo "Could not find FUEL installer IP"
            exit 1
        fi
        export BRANCH="${BRANCH:-master}"
        export BUILD_TAG="${BUILD_TAG:-baremetal}"
        SSH_KEY="-s /var/lib/opnfv/mcp.rsa"
        mkdir -p ../docker-compose/certs
        CA_CERT="-o ../docker-compose/certs/mcp_os_cacert"
        ;;
    apex)
        INSTALLER_IP=$(sudo virsh domifaddr undercloud | grep ipv4 | awk '{print $4}' | cut -d/ -f1)
        if [ -z "${INSTALLER_IP}" ] ; then
            echo "Could not find Apex installer IP"
            exit 1
        fi
        ;;
    *)
        echo "Unknown installer ${INSTALLER}"
        exit 1
esac

if [ ! -z "${INSTALLER_IP}" ]
then
    CMD="./job/releng/utils/fetch_os_creds.sh -i $INSTALLER -a $INSTALLER_IP $CA_CERT $SSH_KEY -d job/openstack.rc"
    echo $CMD
    $CMD

    echo export OS_PROJECT_NAME=admin >> job/openstack.rc
fi

awk '/export / { gsub(/"/, x); print $2}' job/openstack.rc > job/admin.rc
echo "INSTALLER_TYPE=${INSTALLER}" >> job/admin.rc
