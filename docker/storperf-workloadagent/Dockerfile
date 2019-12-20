##############################################################################
# Copyright (c) 2019 VMware and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
#   Docker container for workload
#
# Purpose: docker image for Storperf to control as a synthetic workload
#
# Maintained by Mark Beierl
# Build:
#    $ docker build -t opnfv/storperf-workloadagent:tag .
#

ARG ARCH=x86_64
ARG ALPINE_VERSION=v3.10
FROM multiarch/alpine:$ARCH-$ALPINE_VERSION

RUN apk add --no-cache --upgrade \
	logrotate \
	openssh-client \
	openssh-server \
	sudo

RUN sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/g' /etc/ssh/sshd_config
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/g' /etc/ssh/sshd_config

RUN echo "root ALL=(ALL) ALL" >> /etc/sudoers
RUN ssh-keygen -f /etc/ssh/ssh_host_rsa_key -N '' -t rsa
RUN ssh-keygen -f /etc/ssh/ssh_host_dsa_key -N '' -t dsa

RUN echo root:password | chpasswd

CMD /usr/sbin/sshd -D -e