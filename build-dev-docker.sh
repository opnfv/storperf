#!/bin/bash

echo "Creating a docker image from the current working directory..."

sed "s|RUN git clone https://gerrit.opnfv.org/gerrit/storperf.*$|COPY . \${repos_dir}/storperf|" docker/Dockerfile > Dockerfile
sed -i  "s|COPY storperf.pp|COPY docker/storperf.pp|" Dockerfile
sed -i  "s|COPY supervisord.conf|COPY docker/supervisord.conf|" Dockerfile

docker build -t opnfv/storperf:dev .

rm Dockerfile
