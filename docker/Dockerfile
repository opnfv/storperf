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
ENV DEBIAN_FRONTEND noninteractive

WORKDIR /home/opnfv

# Packaged dependencies
RUN apt-get update && apt-get install -y \
libaio1 \
libaio-dev \
zlib1g-dev \
supervisor \
ssh \
libssl-dev \
libffi-dev \
rsync \
git \
wget \
puppet \
build-essential \
python-dev \
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

# Graphite installation
RUN echo 'deb http://us.archive.ubuntu.com/ubuntu/ trusty universe' >> /etc/apt/sources.list
RUN apt-get -y update

# Install required packages
RUN apt-get -y install python-ldap python-cairo python-django python-twisted python-django-tagging python-simplejson python-memcache python-pysqlite2 python-support python-tz python-pip gunicorn supervisor nginx-light
RUN pip install whisper==0.9.15
RUN pip install --install-option="--prefix=/var/lib/graphite" --install-option="--install-lib=/var/lib/graphite/lib" carbon==0.9.15
RUN pip install --install-option="--prefix=/var/lib/graphite" --install-option="--install-lib=/var/lib/graphite/webapp" graphite-web==0.9.15

# Add system service config
ADD graphite/nginx.conf /etc/nginx/nginx.conf

# Add graphite config
ADD graphite/initial_data.json /var/lib/graphite/webapp/graphite/initial_data.json
ADD graphite/local_settings.py /var/lib/graphite/webapp/graphite/local_settings.py
ADD graphite/carbon.conf /var/lib/graphite/conf/carbon.conf
ADD graphite/storage-schemas.conf /var/lib/graphite/conf/storage-schemas.conf
RUN mkdir -p /opt/graphite/storage
RUN ln -s /var/lib/graphite/storage/whisper /opt/graphite/storage/whisper
RUN touch /var/lib/graphite/storage/graphite.db /var/lib/graphite/storage/index
RUN chown -R www-data /var/lib/graphite/storage
RUN chmod 0775 /var/lib/graphite/storage /var/lib/graphite/storage/whisper
RUN chmod 0664 /var/lib/graphite/storage/graphite.db
RUN cd /var/lib/graphite/webapp/graphite && python manage.py syncdb --noinput

# Git configuration

RUN git config --global http.sslVerify false
RUN git clone --depth 1 -b $BRANCH https://gerrit.opnfv.org/gerrit/storperf ${repos_dir}/storperf
RUN git clone --depth 1 https://gerrit.opnfv.org/gerrit/releng ${repos_dir}/releng

# Third party git fetches

RUN git clone http://git.kernel.dk/fio.git ${repos_dir}/fio
RUN cd ${repos_dir}/fio && git checkout tags/fio-2.2.10
RUN cd ${repos_dir}/fio && make install


RUN chmod 600 ${repos_dir}/storperf/storperf/resources/ssh/storperf_rsa

RUN pip install --upgrade setuptools==33.1.1
RUN pip install -r ${repos_dir}/storperf/docker/requirements.pip


# Open access to SSH if desired
EXPOSE 22

# Graphite
EXPOSE 8000

# ReST API
EXPOSE 5000

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
CMD ["/usr/bin/supervisord"]
