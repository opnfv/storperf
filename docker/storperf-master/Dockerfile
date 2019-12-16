##############################################################################
# Copyright (c) 2015 EMC and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
#   Docker container for STORPERF
#
# Purpose: docker image for Storperf project
#
# Maintained by Jose Lausuch, Mark Beierl
# Build:
#    $ docker build -t opnfv/storperf-master:tag .
#

ARG ARCH=x86_64
ARG ALPINE_VERSION=v3.10
FROM multiarch/alpine:$ARCH-$ALPINE_VERSION as storperf-builder

RUN ulimit -n 1024

LABEL version="8.0" description="OPNFV Storperf Docker container"

ARG BRANCH=master

ENV repos_dir /home/opnfv/repos

RUN apk --no-cache add --update \
    git \
    alpine-sdk \
    coreutils \
    linux-headers \
    libaio \
    libaio-dev \
    zlib-dev

# Third party git fetches
RUN git config --global http.sslVerify false
RUN git clone http://git.kernel.dk/fio.git ${repos_dir}/fio
RUN cd ${repos_dir}/fio && git checkout tags/fio-2.99
RUN cd ${repos_dir}/fio && EXTFLAGS="-static" make -j $(grep -c ^processor /proc/cpuinfo) install

# Build StorPerf

RUN apk --no-cache add --update \
    libffi-dev \
    libressl-dev \
    python3=3.7.5-r1 \
    python3-dev=3.7.5-r1 \
    alpine-sdk \
    linux-headers

# Install StorPerf

COPY requirements.pip /storperf/
RUN python3 -m pip  install --upgrade setuptools==33.1.1
RUN python3 -m pip  install -r /storperf/requirements.pip

# Build stripped down StorPerf image

FROM multiarch/alpine:$ARCH-$ALPINE_VERSION as storperf-master

RUN apk --no-cache add --update \
    libressl-dev \
    python3=3.7.5-r1 \
    bash

COPY --from=storperf-builder /usr/lib/python3.7/site-packages /usr/lib/python3.7/site-packages
COPY --from=storperf-builder /usr/local/bin/fio /usr/local/bin/fio
COPY . /storperf

WORKDIR /storperf
RUN chmod 600 storperf/resources/ssh/storperf_rsa

# ReST API

EXPOSE 5000

# Entry point
CMD [ "python3", "./rest_server.py" ]
