########################################
#   Docker container for STORPERF
########################################
# Purpose: docker image for Storperf project
#
# Maintained by Jose Lausuch, Mark Beierl
# Build:
#    $ docker build -t opnfv/storperf:tag .
#
# Execution:
#    $ docker run -t -i opnfv/storperf /bin/bash
#


FROM ubuntu:14.04
MAINTAINER Jose Lausuch <jose.lausuch@ericsson.com>
LABEL version="0.1" description="OPNFV Storperf Docker container"

ENV repos_dir /home/opnfv/repos

WORKDIR /home/opnfv

# Packaged dependencies
RUN apt-get update && apt-get install -y \
ssh \
rsync \
git \
wget \
puppet \
build-essential \
python-dev \
python-pip \
--no-install-recommends

RUN mkdir -p ${repos_dir}
RUN mkdir -p /root/.ssh
RUN chmod 700 /root/.ssh

RUN git config --global http.sslVerify false
RUN git clone https://gerrit.opnfv.org/gerrit/storperf ${repos_dir}/storperf
RUN git clone https://gerrit.opnfv.org/gerrit/releng ${repos_dir}/releng
RUN git clone git://git.kernel.dk/fio.git ${repos_dir}/fio
RUN cd ${repos_dir}/fio && git checkout tags/fio-2.2.10
RUN cd ${repos_dir}/fio &&  make
