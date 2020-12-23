##############################################################################
# Copyright (c) 2017 Dell EMC and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
#   Docker container for StorPerf Graphing and Reporting module
#
# Purpose: self-contained image that can create reports and graphs of data
#
# Build:
#    $ docker build -t opnfv/storperf-reporting:tag .
##


ARG ARCH=x86_64
ARG ALPINE_VERSION=v3.10
FROM multiarch/alpine:$ARCH-$ALPINE_VERSION
MAINTAINER Mark Beierl <mark.beierl@dell.com>
LABEL version="8.0" description="OPNFV Storperf Reporting Container"

ARG BRANCH=master

RUN ulimit -n 1024

RUN apk add --update python3=3.7.5-r1

COPY . /home/opnfv/storperf-reporting
WORKDIR /home/opnfv/storperf-reporting/src

RUN python3 -m pip install --no-cache-dir -r /home/opnfv/storperf-reporting/requirements.txt

CMD ["python3", "app.py"]

EXPOSE 5000
