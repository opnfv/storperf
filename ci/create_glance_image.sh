#!/bin/bash
##############################################################################
# Copyright (c) 2017 EMC and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

cd "$(dirname "$0")" || exit
mkdir -p job

ARCH="${ARCH:-$(uname -m)}"

IMAGE_NAME="Ubuntu 17.04 ${ARCH}"

echo "Checking for ${IMAGE_NAME} in Glance"

IMAGE="$(openstack image list | grep "${IMAGE_NAME}")"
PROPERTIES=""
if [ -z "$IMAGE" ]
then

    case "${ARCH}" in
    aarch64)
        FILE=ubuntu-17.04-server-cloudimg-arm64.img
        PROPERTIES="--property hw_firmware_type=uefi --property hw_video_model=vga"
        ;;
    armhf)
        FILE=ubuntu-17.04-server-cloudimg-armhf.img
        ;;
    x86_64)
        FILE=ubuntu-17.04-server-cloudimg-amd64.img
        ;;
    *)
        echo "Unsupported architecture: ${ARCH}"
        exit 1
        ;;
    esac

    wget --continue -q "https://cloud-images.ubuntu.com/releases/17.04/release/${FILE}"
    openstack image create "${IMAGE_NAME}" --disk-format qcow2 --public \
    ${PROPERTIES} \
    --container-format bare --file "${FILE}"
fi

openstack image show "${IMAGE_NAME}"

echo "${IMAGE_NAME}" > job/glance_image_name
