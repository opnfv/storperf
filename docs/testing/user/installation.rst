.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0
.. (c) OPNFV, Dell EMC and others.

===========================
StorPerf Installation Guide
===========================

OpenStack Prerequisites
===========================
If you do not have an Ubuntu 16.04 image in Glance, you will need to add one.
You also need to create the StorPerf flavor, or choose one that closely
matches.  For Ubuntu 16.04, it must have a minimum of a 4 GB disk.  It should
also have about 8 GB RAM to support FIO's memory mapping of written data blocks
to ensure 100% coverage of the volume under test.

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

You must have your OpenStack Controller environment variables defined and passed to
the StorPerf container. The easiest way to do this is to put the rc file contents
into a clean file called admin.rc that looks similar to this for V2 authentication:

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

#. Run container on bare metal
#. Run container in a VM

Requirements:

* Docker and docker-compose must be installed
  * (note: sudo_ may be required if user is not part of docker group)
* OpenStack Controller credentials are available
* Host has access to the OpenStack Controller API
* Host must have internet connectivity for downloading docker image
* Enough OpenStack floating IPs must be available to match your agent count
* A local directory for holding the Carbon DB Whisper files

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
* 8000 for StorPerf's Graphite Web Server


Running StorPerf Container
==========================

**As of Euphrates (development) release (June 2017), StorPerf has
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

     968c0c2d7c0e24f6777c33b37d9b4fd885575155069fb760405ec8214b2eb672  docker-compose.yaml

To run, you must specify two environment variables:

* ENV_FILE, which points to your OpenStack admin.rc as noted above.
* CARBON_DIR, which points to a directory that will be mounted to store the raw metrics.
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

     00649e02237d27bf0b40d1a66160a68a56c9f5e1ceb78d7858e30715cf4350e3  create-compose.py



Docker Exec
~~~~~~~~~~~

If needed, the container can be entered with docker exec.  This is not normally
required.

.. code-block:: console

    docker exec -it storperf-master bash



Pulling StorPerf Container
==========================

Master (Euphrates)
~~~~~~~~~~~~~~~~~~

StorPerf has switched to docker-compose in the latest version.  The tag for
pulling the latest master Euphrates container is:

.. code-block:: bash

   docker pull opnfv/storperf-master:latest
   docker pull opnfv/storperf-reporting:latest
   docker pull opnfv/storperf-httpfrontend:latest

However, by itself, this will no longer provide full functionality.  Full
instructions are provided in the Running StorPerf Container section of this
document.


Danube
~~~~~~

The tag for the latest stable Danube is be:

.. code-block:: bash

   docker pull opnfv/storperf:danube.3.0

Colorado
~~~~~~~~

The tag for the latest stable Colorado release is:

.. code-block:: bash

   docker pull opnfv/storperf:colorado.0.1

Brahmaputra
~~~~~~~~~~~

The tag for the latest stable Brahmaputra release is:

.. code-block:: bash

   docker pull opnfv/storperf:brahmaputra.1.2

StorPerf on ARM Processors
==========================

StorPerf now supports docker images on ARM processors as well. However, at the moment
there is no upstream image on DockerHub. The user needs to manually build it. Firstly,
clone StorPerf repository from GitHub

.. code-block:: bash

  git clone https://git.opnfv.org/storperf
  cd storperf/docker/

Next, build and setup the docker images

.. code-block:: console

  TAG=aarch64 ENV_FILE=./admin.rc CARBON_DIR=./carbon docker-compose -f local-docker-compose.yaml build
  TAG=aarch64 ENV_FILE=./admin.rc CARBON_DIR=./carbon docker-compose -f local-docker-compose.yaml up -d
