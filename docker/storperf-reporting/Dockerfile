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


FROM alpine:3.1
MAINTAINER Mark Beierl <mark.beierl@dell.com>
LABEL version="0.1" description="OPNFV Storperf Reporting Container"

RUN apk add --update python py-pip

COPY . /home/opnfv/storperf-reporting
WORKDIR /home/opnfv/storperf-reporting
RUN pip install -r /home/opnfv/storperf-reporting/requirements.txt

CMD ["python", "app.py"]

EXPOSE 5000