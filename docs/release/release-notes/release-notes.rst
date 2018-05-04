.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0


This document provides the release notes for Fraser 2.0 of StorPerf.

.. contents::
   :depth: 3
   :local:


Version history
===============


+--------------------+--------------------+--------------------+--------------------+
| **Date**           | **Ver.**           | **Author**         | **Comment**        |
|                    |                    |                    |                    |
+--------------------+--------------------+--------------------+--------------------+
| 2018-04-18         | Fraser 1.0         | Mark Beierl        |                    |
|                    |                    |                    |                    |
+--------------------+--------------------+--------------------+--------------------+
| 2018-05-18         | Fraser 2.0         | Mark Beierl        |                    |
|                    |                    |                    |                    |
+--------------------+--------------------+--------------------+--------------------+


Important notes
----------------

StorPerf has added the ability to specify the number of Cinder Volumes per
agent VM to test.  The name of the device that the volume is attached to
has been appended to the host IP address in the metrics so that it can be
tracked independently.


Summary
--------

StorPerf is a standalone framework that uses OpenStack to measure Cinder volume
performance.  If desired, it can push results to the OPNFV Test Results DB, or
the embedded Graphite web interface can be used to perform ad hoc queries.

This release allows for changing of stack attributes from the OpenStack CLI.
Using a command such as

.. code-block::
  heat stack-update StorPerfAgentGroup --existing -P "agent_count=6"

will change the existing stack to use 6 agents.  Note that StorPerf can take
up to 1 minute after the stack update is complete before detecting the new
values.  Please use a GET of the configurations API to test for updated
values prior to submitting a new test.

The following command changes the number of volumes per agent:

.. code-block::
  heat stack-update StorPerfAgentGroup --existing -P "volume_count=2"


Release Data
-------------

+--------------------------------------+--------------------------------------+
| **Project**                          | StorPerf                             |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| **Repo/commit-ID**                   | storperf/fraser.2.0                  |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| **Release designation**              | Fraser base release                  |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| **Release date**                     | 2018-05-18                           |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| **Purpose of the delivery**          | OPNFV Fraser release 2.0             |
|                                      |                                      |
+--------------------------------------+--------------------------------------+

Version change
===============

Module version changes
-----------------------

No changes to any modules.

Reason for version
===================

Features additions
-------------------

* STORPERF-242 - Allow user to change stack parameters outside of StorPerf


Bug Fixes
----------

Deliverables
=============

Software
---------

- `StorPerf master image <https://hub.docker.com/r/opnfv/storperf-master/>`_
  (tag: x86_64-fraser.2.0  or aarch64-fraser.2.0)

- `StorPerf swaggerui <https://hub.docker.com/r/opnfv/storperf-swaggerui/>`_
  (tag: x86_64-fraser.2.0  or aarch64-fraser.2.0)

- `StorPerf graphite image <https://hub.docker.com/r/opnfv/storperf-graphite/>`_
  (tag: x86_64-fraser.2.0  or aarch64-fraser.2.0)

- `StorPerf reporting image <https://hub.docker.com/r/opnfv/storperf-reporting/>`_
  (tag: x86_64-fraser.2.0  or aarch64-fraser.2.0)

- `StorPerf Http-Frontend image <https://hub.docker.com/r/opnfv/storperf-httpfrontend/>`_
  (tag: x86_64-fraser.2.0  or aarch64-fraser.2.0)

Documentation
--------------

- `User Guide <http://docs.opnfv.org/en/latest/submodules/storperf/docs/testing/user/index.html>`_

Known Limitations, Issues and Workarounds
------------------------------------------

Limitations
============



Known issues
=============

* Cirros target VMs do not always mount Cinder volumes on first boot.  Sometimes
  a reboot of the VM is required to properly attach the Cinder volume to /dev/vdb
* A bug in the linux kernel can prevent Cinder volumes from attaching to VMs
  using ARM architecture.  Specifying the following properties in Glance for
  the ARM based image will work around this problem.  Note: this will cause
  the device to show up as a SCSI device and therefore will be /dev/sdb instead
  of /dev/vdb.

.. code-block:
  --property hw_disk_bus=scsi --property hw_scsi_model=virtio-scsi


Test Result
===========

- `OPNFV Test Results DB <http://testresults.opnfv.org/reporting/fraser/storperf/status-apex.html>`_
