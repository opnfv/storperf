##############################################################################
# Copyright (c) 2017 Dell EMC and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
#   Docker container for StorPerf HTTP Graphite
#
# Build:
#    $ docker build -t opnfv/storperf-graphite:tag .
##

# From https://github.com/SchweizerischeBundesbahnen/docker-graphite

ARG ARCH=x86_64
ARG ALPINE_VERSION=v3.5
FROM multiarch/alpine:$ARCH-$ALPINE_VERSION

RUN ulimit -n 1024

# Install basic stuff =)
RUN apk add --no-cache \
  bash \
  ca-certificates \
  nginx \
  openssl \
  py2-pip \
  supervisor \
  tini \
  && pip install --no-cache-dir \
  supervisor-stdout \
  gunicorn

# Install graphite
ENV GRAPHITE_ROOT /opt/graphite

RUN apk add --no-cache \
  alpine-sdk \
  fontconfig \
  libffi \
  libffi-dev \
  python-dev \
  py-cairo \
  && export PYTHONPATH="/opt/graphite/lib/:/opt/graphite/webapp/" \
  && pip install https://github.com/graphite-project/whisper/tarball/master \
  && pip install https://github.com/graphite-project/carbon/tarball/master \
  && pip install https://github.com/graphite-project/graphite-web/tarball/master \
  && apk del \
  alpine-sdk \
  python-dev \
  libffi-dev

EXPOSE 8080
EXPOSE 2003
EXPOSE 2004
EXPOSE 7002

VOLUME ["/opt/graphite/conf", "/opt/graphite/storage"]

COPY run.sh /run.sh
COPY etc/ /etc/
COPY conf/ /opt/graphite/conf.example/

# Enable tiny init
ENTRYPOINT ["/sbin/tini", "--"]
CMD ["/bin/bash", "/run.sh"]
