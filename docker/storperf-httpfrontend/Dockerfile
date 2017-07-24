##############################################################################
# Copyright (c) 2017 Dell EMC and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
#   Docker container for StorPerf HTTP Front ENd
#
# Build:
#    $ docker build -t opnfv/storperf-frontend:tag .
##


FROM nginx:stable-alpine
MAINTAINER Mark Beierl <mark.beierl@dell.com>
LABEL version="3.1" description="OPNFV Storperf HTTP Front End Container"

ARG BRANCH=master

COPY ./nginx.conf /etc/nginx/nginx.conf
COPY ./html /etc/nginx/html

EXPOSE 5000
