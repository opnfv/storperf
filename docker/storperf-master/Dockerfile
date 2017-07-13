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

FROM ubuntu:14.04
MAINTAINER Jose Lausuch <jose.lausuch@ericsson.com>
LABEL version="5.0" description="OPNFV Storperf Docker container"

ENV repos_dir /home/opnfv/repos
ENV DEBIAN_FRONTEND noninteractive

WORKDIR /home/opnfv

# Needed for Graphite installation
RUN echo 'deb http://us.archive.ubuntu.com/ubuntu/ trusty universe' >> /etc/apt/sources.list

# Packaged dependencies
RUN apt-get update && apt-get install -y \
libaio1 \
libaio-dev \
zlib1g-dev \
supervisor \
libssl-dev \
libffi-dev \
git \
build-essential \
python-dev \
python-pip \
--no-install-recommends

RUN mkdir -p /root/.ssh
RUN chmod 700 /root/.ssh

# Install required packages

RUN apt-get -y install python-ldap python-cairo python-django python-twisted python-django-tagging python-simplejson python-memcache python-pysqlite2 python-support python-tz python-pip gunicorn supervisor nginx-light
RUN pip install whisper==0.9.15
RUN pip install --install-option="--prefix=/var/lib/graphite" --install-option="--install-lib=/var/lib/graphite/lib" carbon==0.9.15
RUN pip install --install-option="--prefix=/var/lib/graphite" --install-option="--install-lib=/var/lib/graphite/webapp" graphite-web==0.9.15

# Add graphite config

ADD graphite/nginx.conf /etc/nginx/nginx.conf
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


# Third party git fetches

RUN git config --global http.sslVerify false
RUN git clone http://git.kernel.dk/fio.git ${repos_dir}/fio
RUN cd ${repos_dir}/fio && git checkout tags/fio-2.2.10
RUN cd ${repos_dir}/fio && make install


# Install StorPerf

COPY . ${repos_dir}/storperf
RUN chmod 600 ${repos_dir}/storperf/storperf/resources/ssh/storperf_rsa
RUN pip install --upgrade setuptools==33.1.1
RUN pip install -r ${repos_dir}/storperf/requirements.pip
COPY ./supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Graphite
EXPOSE 8000

# ReST API
EXPOSE 5000

CMD ["/usr/bin/supervisord"]
