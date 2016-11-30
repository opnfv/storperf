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
#    $ docker build -t opnfv/storperf:tag .
#
# Execution:
#    $ docker run -t opnfv/storperf /bin/bash
#


FROM ubuntu:14.04
MAINTAINER Jose Lausuch <jose.lausuch@ericsson.com>
LABEL version="0.1" description="OPNFV Storperf Docker container"

ARG BRANCH=master

ENV repos_dir /home/opnfv/repos

WORKDIR /home/opnfv

# Packaged dependencies
RUN apt-get update && apt-get install -y \
libaio1 \
libaio-dev \
zlib1g-dev \
supervisor \
ssh \
rsync \
git \
wget \
puppet \
build-essential \
python-dev \
python-matplotlib \
python-pip \
--no-install-recommends


# Allow root SSH access with 'storperf' as the password

RUN echo 'root:storperf' | chpasswd
RUN sed -i 's/PermitRootLogin without-password/PermitRootLogin yes/' /etc/ssh/sshd_config

# SSH login fix. Otherwise user is kicked off after login
RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd

ENV NOTVISIBLE "in users profile"
RUN echo "export VISIBLE=now" >> /etc/profile
RUN mkdir -p /var/run/sshd

RUN mkdir -p ${repos_dir}
RUN mkdir -p /root/.ssh
RUN chmod 700 /root/.ssh

RUN git config --global http.sslVerify false
RUN git --depth 1 -b $BRANCH clone https://gerrit.opnfv.org/gerrit/storperf ${repos_dir}/storperf
RUN git --depth 1 clone https://gerrit.opnfv.org/gerrit/releng ${repos_dir}/releng

# Third party git fetches
RUN git clone https://github.com/swagger-api/swagger-ui.git ${repos_dir}/swagger-ui
RUN mkdir -p ${repos_dir}/storperf/storperf/resources/html/swagger
RUN cp -r ${repos_dir}/swagger-ui/dist/* ${repos_dir}/storperf/storperf/resources/html/swagger
RUN sed -i 's|url = "http://petstore.swagger.io/v2/swagger.json";|url = window.location.protocol+"//"+window.location.host+"/api/spec.json";|' ${repos_dir}/storperf/storperf/resources/html/swagger/index.html

RUN git clone http://git.kernel.dk/fio.git ${repos_dir}/fio
RUN cd ${repos_dir}/fio && git checkout tags/fio-2.2.10
RUN cd ${repos_dir}/fio && make -j 6 install

RUN puppet module install gdsoperations-graphite

RUN chmod 600 ${repos_dir}/storperf/storperf/resources/ssh/storperf_rsa

RUN pip install -r ${repos_dir}/storperf/docker/requirements.pip

COPY storperf.pp /etc/puppet/manifests/storperf.pp
RUN puppet apply /etc/puppet/manifests/storperf.pp

RUN ln -s /opt/graphite/lib/whisper* /usr/lib/python2.7/

# Open access to SSH if desired
EXPOSE 22

# Graphite
EXPOSE 8000

# ReST API
EXPOSE 5000

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
CMD ["/usr/bin/supervisord"]
