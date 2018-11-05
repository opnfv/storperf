.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0
.. (c) OPNFV, Dell EMC and others.

===========================
StorPerf Installation Guide
===========================

OpenStack Prerequisites
===========================
StorPerf can be instructed to use OpenStack APIs in order to manage a
Heat stack of virtual machines and Cinder volumes, or it can be run in
stackless mode, where it does not need to know anything about OpenStack.

When running in OpenStack mode, there will need to be an external network
with floating IPs available to assign to the VMs, as well as a Glance image
that can be used to boot the VMs.  This can be almost any Linux based
image, as long as it can either accept OpenStack metadata for injecting
the SSH key, or it has known SSH credentials as part of the base image.

The flavor for the image should provide enough disk space for the initial
boot, along with additional space if profiling of the Glance backing is
desired.  It should also provide at least 8 GB RAM to support FIO's memory
mapping of written data blocks.

There are scripts in storperf/ci directory to assist, or you can use the follow
code snippets:

.. code-block:: bash

    # Put an Ubuntu Image in glance
    wget -q https://cloud-images.ubuntu.com/releases/16.04/release/ubuntu-16.04-server-cloudimg-amd64-disk1.img
    openstack image create "Ubuntu 16.04 x86_64" --disk-format qcow2 --public \
        --container-format bare --file ubuntu-16.04-server-cloudimg-amd64-disk1.img

    # Create StorPerf flavor
    openstack flavor create storperf \
        --id auto \
        --ram 8192 \
        --disk 4 \
        --vcpus 2

OpenStack Credentials
~~~~~~~~~~~~~~~~~~~~~

Unless running in stackless mode, the OpenStack Controller environment
variables must be defined and passed to the StorPerf container. The easiest
way to do this is to put the rc file contents into a clean file called
admin.rc that looks similar to this for V2 authentication:

.. code-block:: console

   cat << 'EOF' > admin.rc
   OS_AUTH_URL=http://10.13.182.243:5000/v2.0
   OS_TENANT_ID=e8e64985506a4a508957f931d1800aa9
   OS_TENANT_NAME=admin
   OS_PROJECT_NAME=admin
   OS_USERNAME=admin
   OS_PASSWORD=admin
   OS_REGION_NAME=RegionOne
   EOF

For V3 authentication, at a minimum, use the following:

.. code-block:: console

   cat << 'EOF' > admin.rc
   OS_AUTH_URL=http://10.10.243.14:5000/v3
   OS_USERNAME=admin
   OS_PASSWORD=admin
   OS_PROJECT_DOMAIN_NAME=Default
   OS_PROJECT_NAME=admin
   OS_USER_DOMAIN_NAME=Default
   EOF


Additionally, if you want your results published to the common OPNFV Test Results
DB, add the following:

.. code-block:: console

    TEST_DB_URL=http://testresults.opnfv.org/testapi


Planning
========

StorPerf is delivered as a series of Docker containers managed by
docker-compose.  There are two possible methods for installation:

#. Run the containers on bare metal
#. Run the containers in a VM

Requirements:

* Docker and docker-compose must be installed
  * (note: sudo_ may be required if user is not part of docker group)
* OpenStack Controller credentials are available
* Host has access to the OpenStack Controller API
* Host must have internet connectivity for downloading docker image
* Enough OpenStack floating IPs must be available to match your agent count
* Optionally, a local directory for holding the Carbon DB Whisper files

Local disk used for the Carbon DB storage as the default size of the docker
container is only 10g. Here is an example of how to create a local storage
directory and set its permissions so that StorPerf can write to it:

.. code-block:: console

    mkdir -p ./carbon
    sudo chown 33:33 ./carbon


.. _sudo: https://docs.docker.com/engine/reference/run/#general-form

Ports
=====

The following ports are exposed if you use the supplied docker-compose.yaml
file:

* 5000 for StorPerf ReST API and Swagger UI

Note: Port 8000 is no longer exposed and graphite can be accesed via
http://storperf:5000/graphite

Running StorPerf Container
==========================

**As of Euphrates release (June 2017), StorPerf has
changed to use docker-compose in order to start its services.**

Docker compose requires a local file to be created in order to define the
services that make up the full StorPerf application.  This file can be:

* Manually created
* Downloaded from the StorPerf git repo, or
* Create via a helper script from the StorPerf git repo

Manual creation involves taking the sample in the StorPerf git repo and typing
in the contents by hand on your target system.

Downloading From Git Repo
=========================

.. code-block:: console

     wget https://raw.githubusercontent.com/opnfv/storperf/master/docker-compose/docker-compose.yaml
     sha256sum docker-compose.yaml

which should result in:

.. code-block:: console

    69856e9788bec36308a25303ec9154ed68562e126788a47d54641d68ad22c8b9  docker-compose.yaml

To run, you must specify two environment variables:

* ENV_FILE, which points to your OpenStack admin.rc as noted above.  If running
  in stackless mode only, it is possible to remove the ENV_FILE reference from
  the docker-compose.yaml file.
* CARBON_DIR, which points to a directory that will be mounted to store the
  raw metrics.  If desired, the CARBON_DIR can be removed from the
  docker-compose.yaml file, causing metrics to be kept in the container only.
* TAG, which specified the Docker tag for the build (ie: latest, danube.3.0, etc).

The following command will start all the StorPerf services:

.. code-block:: console

     TAG=latest ENV_FILE=./admin.rc CARBON_DIR=./carbon/ docker-compose pull
     TAG=latest ENV_FILE=./admin.rc CARBON_DIR=./carbon/ docker-compose up -d

StorPerf is now available at http://docker-host:5000/


Downloading Helper Tool
=======================

A tool to help you get started with the docker-compose.yaml can be downloaded
from:

.. code-block:: console

     wget https://raw.githubusercontent.com/opnfv/storperf/master/docker-compose/create-compose.py
     sha256sum create-compose.py

which should result in:

.. code-block:: console

     327cad2a7b3a3ca37910978005c743799313c2b90709e4a3f142286a06e53f57  create-compose.py

Note: The script will run fine on python3. Install python future package to avoid error on python2.

.. code-block:: console

     pip install future


Docker Exec
~~~~~~~~~~~

If needed, any StorPerf container can be entered with docker exec.  This is not normally
required.

.. code-block:: console

    docker exec -it storperf-master /bin/bash



Pulling StorPerf Containers
===========================

The tags for StorPerf can be found here: https://hub.docker.com/r/opnfv/storperf-master/tags/

Master (latest)
~~~~~~~~~~~~~~~

This tag represents  StorPerf at its most current state of development.  While
self-tests have been run, there is not a guarantee that all features will be
functional, or there may be bugs.

Documentation for latest can be found using the latest label at:

:ref:`User Guide <storperf-userguide>`

For x86_64 based systems, use:

.. code-block:: console

    TAG=x86_64-latest ENV_FILE=./admin.rc CARBON_DIR=./carbon/ docker-compose pull
    TAG=x86_64-latest ENV_FILE=./admin.rc CARBON_DIR=./carbon/ docker-compose up -d

For 64 bit ARM based systems, use:

.. code-block:: console

    TAG=aarch64-latest ENV_FILE=./admin.rc CARBON_DIR=./carbon/ docker-compose pull
    TAG=aarch64-latest ENV_FILE=./admin.rc CARBON_DIR=./carbon/ docker-compose up -d


Release (stable)
~~~~~~~~~~~~~~~~

This tag represents StorPerf at its most recent stable release.  There are
no known bugs and known issues and workarounds are documented in the release
notes.  Issues found here should be reported in JIRA:

https://jira.opnfv.org/secure/RapidBoard.jspa?rapidView=3

For x86_64 based systems, use:

.. code-block:: console

    TAG=x86_64-stable ENV_FILE=./admin.rc CARBON_DIR=./carbon/ docker-compose pull
    TAG=x86_64-stable ENV_FILE=./admin.rc CARBON_DIR=./carbon/ docker-compose up -d

For 64 bit ARM based systems, use:

.. code-block:: console

    TAG=aarch64-stable ENV_FILE=./admin.rc CARBON_DIR=./carbon/ docker-compose pull
    TAG=aarch64-stable ENV_FILE=./admin.rc CARBON_DIR=./carbon/ docker-compose up -d



Fraser (opnfv-6.0.0)
~~~~~~~~~~~~~~~~~~

This tag represents the 6th OPNFV release and the 5th StorPerf release.  There
are no known bugs and known issues and workarounds are documented in the release
notes.  Documentation can be found under the Fraser label at:

http://docs.opnfv.org/en/stable-fraser/submodules/storperf/docs/testing/user/index.html

Issues found here should be reported against release 6.0.0 in JIRA:

https://jira.opnfv.org/secure/RapidBoard.jspa?rapidView=3

For x86_64 based systems, use:

.. code-block:: console

    TAG=x86_64-opnfv-6.0.0 ENV_FILE=./admin.rc CARBON_DIR=./carbon/ docker-compose pull
    TAG=x86_64-opnfv-6.0.0 ENV_FILE=./admin.rc CARBON_DIR=./carbon/ docker-compose up -d

For 64 bit ARM based systems, use:

.. code-block:: console

    TAG=aarch64-opnfv-6.0.0 ENV_FILE=./admin.rc CARBON_DIR=./carbon/ docker-compose pull
    TAG=aarch64-opnfv-6.0.0 ENV_FILE=./admin.rc CARBON_DIR=./carbon/ docker-compose up -d



Euphrates (opnfv-5.0.0)
~~~~~~~~~~~~~~~~~

This tag represents the 5th OPNFV release and the 4th StorPerf release.  There
are no known bugs and known issues and workarounds are documented in the release
notes.  Documentation can be found under the Euphrates label at:

http://docs.opnfv.org/en/stable-euphrates/submodules/storperf/docs/testing/user/index.html

Issues found here should be reported against release 6.0.0 in JIRA:

https://jira.opnfv.org/secure/RapidBoard.jspa?rapidView=3

For x86_64 based systems, use:

.. code-block:: console

    TAG=x86_64-opnfv-6.0.0 ENV_FILE=./admin.rc CARBON_DIR=./carbon/ docker-compose pull
    TAG=x86_64-opnfv-6.0.0 ENV_FILE=./admin.rc CARBON_DIR=./carbon/ docker-compose up -d

For 64 bit ARM based systems, use:

.. code-block:: console

    TAG=aarch64-opnfv-6.0.0 ENV_FILE=./admin.rc CARBON_DIR=./carbon/ docker-compose pull
    TAG=aarch64-opnfv-6.0.0 ENV_FILE=./admin.rc CARBON_DIR=./carbon/ docker-compose up -d
