#!/bin/bash
##############################################################################
# Copyright (c) 2015 EMC and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

echo "Creating a docker image from the current working directory..."

sed "s|RUN git clone https://gerrit.opnfv.org/gerrit/storperf.*$|COPY . \${repos_dir}/storperf|" docker/Dockerfile > Dockerfile
sed -i  "s|COPY storperf.pp|COPY docker/storperf.pp|" Dockerfile
sed -i  "s|COPY supervisord.conf|COPY docker/supervisord.conf|" Dockerfile

docker build -t opnfv/storperf:dev .

rm -f Dockerfile
