#!/bin/bash
##############################################################################
# Copyright (c) 2017 EMC and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

if [ -z "${ARCH}" ]
then
    ARCH="$(uname -m)"
fi

IMAGE_NAME="Ubuntu 16.04 ${ARCH}"

echo "Checking for ${IMAGE_NAME} in Glance"

IMAGE="$(openstack image list | grep "${IMAGE_NAME}")"
if [ -z "$IMAGE" ]
then

    case ${ARCH} in
    aarch64)
        FILE=ubuntu-16.04-server-cloudimg-arm64-disk1.img
        ;;
    armhf)
        FILE=ubuntu-16.04-server-cloudimg-armhf-disk1.img
        ;;
    x86_64)
        FILE=ubuntu-16.04-server-cloudimg-amd64-disk1.img
        ;;
    *)
        echo "Unsupported architecture: ${ARCH}"
        exit 1
        ;;
    esac

    rm -f ${FILE}
    wget -q "https://cloud-images.ubuntu.com/releases/16.04/release/${FILE}"
    openstack image create "${IMAGE_NAME}" --disk-format qcow2 --public \
    --container-format bare --file "${FILE}"
fi

openstack image show "${IMAGE_NAME}"
