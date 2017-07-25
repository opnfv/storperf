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

FROM alpine:3.5 as fio-builder

MAINTAINER Mark Beierl <mark.beierl@dell.com>
LABEL version="5.0" description="OPNFV Storperf Docker container"

ENV repos_dir /home/opnfv/repos

RUN apk --no-cache add --update \
    python-dev \
    git \
    alpine-sdk \
    linux-headers \
    libaio \
    libaio-dev \
    zlib-dev

# Third party git fetches

RUN git config --global http.sslVerify false
RUN git clone http://git.kernel.dk/fio.git ${repos_dir}/fio
RUN cd ${repos_dir}/fio && git checkout tags/fio-2.2.10
RUN cd ${repos_dir}/fio && EXTFLAGS="-static" make install

# StorPerf Master Builder

FROM alpine:3.5 as storperf-builder

RUN apk --no-cache add --update \
    libffi-dev \
    libressl-dev \
    python \
    py-pip \
    python-dev \
    alpine-sdk \
    linux-headers \
    bash

# Install StorPerf

COPY requirements.pip /storperf/
RUN pip install --upgrade setuptools==33.1.1
RUN pip install -r /storperf/requirements.pip

# Change FROM once we get rid of internal Graphite

FROM alpine:3.5 as storperf-master

RUN apk --no-cache add --update \
    python \
    bash

COPY --from=storperf-builder /usr/lib/python2.7/site-packages /usr/lib/python2.7/site-packages
COPY --from=fio-builder /usr/local/bin/fio /usr/local/bin/fio
COPY . /storperf

WORKDIR /storperf
RUN chmod 600 storperf/resources/ssh/storperf_rsa

# ReST API

EXPOSE 5000

#Graphite
RUN apk --no-cache add --update \
    python \
    py-pip \
    python-dev \
    alpine-sdk \
    py-tz \
    nginx \
    cairo \
    supervisor

RUN deluser xfs

RUN pip install \
    gunicorn==17.5 \
    Django==1.6.11 \
    django-tagging==0.3.1 \
    cairocffi \
    constants \
    zope.interface

RUN adduser -S -g www-data -u 33 www-data

RUN pip install whisper==0.9.15
RUN pip install --install-option="--prefix=/var/lib/graphite" --install-option="--install-lib=/var/lib/graphite/lib" carbon==0.9.15
RUN pip install --install-option="--prefix=/var/lib/graphite" --install-option="--install-lib=/var/lib/graphite/webapp" graphite-web==0.9.15

ADD graphite/nginx.conf /etc/nginx/nginx.conf
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
ADD graphite/initial_data.json /var/lib/graphite/webapp/graphite/initial_data.json
RUN cd /var/lib/graphite/webapp/graphite && python manage.py syncdb --noinput

RUN mkdir -p /var/log/supervisor

COPY ./supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 8000

# Entry point

CMD ["/usr/bin/supervisord"]
