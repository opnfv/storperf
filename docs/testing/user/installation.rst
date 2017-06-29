.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0
.. (c) OPNFV, Dell EMC and others.

===========================
StorPerf Installation Guide
===========================

OpenStack Prerequisites
===========================
If you do not have an Ubuntu 16.04 image in Glance, you will need to add one.
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


Planning
===========================

StorPerf is delivered as a series of `Docker containers
<https://hub.docker.com/r/opnfv/storperf/tags/>`__ managed by
docker-compose.  There are two possible methods for installation:

   1. Run container on bare metal
   2. Run container in a VM

Requirements:

    * Docker and docker-compose must be installed
    * OpenStack Controller credentials are available
    * Host has access to the OpenStack Controller API
    * Host must have internet connectivity for downloading docker image
    * Enough OpenStack floating IPs must be available to match your agent count



Pulling StorPerf Container
==========================

Master (Euphrates)
~~~~~~~~~~~~~~~~~~

StorPerf has switched to docker-compose in the latest version.  The tag for
pulling the latest master Euphrates container is:

.. code-block:: bash

   docker pull opnfv/storperf:master

However, by itself, this will no longer provide full functionality.  Full
instructions are provided in the Introduction document.


Danube
~~~~~~

The tag for the latest stable Danube is be:

.. code-block:: bash

   docker pull opnfv/storperf:danube.2.0

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
