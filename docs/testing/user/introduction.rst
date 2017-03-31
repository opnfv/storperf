.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0
.. (c) OPNFV, Dell EMC and others.

==================================
StorPerf Container Execution Guide
==================================

Planning
========

There are some ports that the container can expose:

    * 22 for SSHD. Username and password are root/storperf. This is used for CLI access only
    * 5000 for StorPerf ReST API.
    * 8000 for StorPerf's Graphite Web Server

OpenStack Credentials
~~~~~~~~~~~~~~~~~~~~~

You must have your OpenStack Controller environment variables defined and passed to
the StorPerf container. The easiest way to do this is to put the rc file contents
into a clean file the looks similar to this for V2 authentication:

.. code-block:: console

    OS_AUTH_URL=http://10.13.182.243:5000/v2.0
    OS_TENANT_ID=e8e64985506a4a508957f931d1800aa9
    OS_TENANT_NAME=admin
    OS_PROJECT_NAME=admin
    OS_USERNAME=admin
    OS_PASSWORD=admin
    OS_REGION_NAME=RegionOne

For V3 authentication, use the following:

.. code-block:: console

   OS_AUTH_URL=http://10.13.182.243:5000/v3
   OS_PROJECT_ID=32ae78a844bc4f108b359dd7320463e5
   OS_PROJECT_NAME=admin
   OS_USER_DOMAIN_NAME=Default
   OS_USERNAME=admin
   OS_PASSWORD=admin
   OS_REGION_NAME=RegionOne
   OS_INTERFACE=public
   OS_IDENTITY_API_VERSION=3

Additionally, if you want your results published to the common OPNFV Test Results
 DB, add the following:

.. code-block:: console

    TEST_DB_URL=http://testresults.opnfv.org/testapi

Running StorPerf Container
==========================

You might want to have the local disk used for storage as the default size of the docker
container is only 10g. This is done with the -v option, mounting under
/opt/graphite/storage/whisper

.. code-block:: console

    mkdir -p ~/carbon
    sudo chown 33:33 ~/carbon

The recommended method of running StorPerf is to expose only the ReST and Graphite
ports.  The command line below shows how to run the container with local disk for
the carbon database.

.. code-block:: console

    docker run -t --env-file admin-rc -p 5000:5000 -p 8000:8000 -v ~/carbon:/opt/graphite/storage/whisper --name storperf opnfv/storperf


Docker Exec
~~~~~~~~~~~

Instead of exposing port 5022 externally, you can use the exec method in docker.  This
provides a slightly more secure method of running StorPerf container without having to
expose port 22.

If needed, the container can be entered with docker exec.  This is not normally required.

.. code-block:: console

    docker exec -it storperf bash

Container with SSH
~~~~~~~~~~~~~~~~~~

Running the StorPerf Container with all ports open and a local disk for the result
storage.  This is not recommended as the SSH port is open.

.. code-block:: console

    docker run -t --env-file admin-rc -p 5022:22 -p 5000:5000 -p 8000:8000 -v ~/carbon:/opt/graphite/storage/whisper --name storperf opnfv/storperf

This will then permit ssh to localhost port 5022 for CLI access.

