.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0


This document provides the release notes for Gambia 1.0 of StorPerf.

.. contents::
   :depth: 3
   :local:


Version history
===============


+--------------------+--------------------+--------------------+--------------------+
| **Date**           | **Ver.**           | **Author**         | **Comment**        |
|                    |                    |                    |                    |
+--------------------+--------------------+--------------------+--------------------+
| 2018-11-09         | Gambia 1.0         | Mark Beierl        |                    |
|                    |                    |                    |                    |
+--------------------+--------------------+--------------------+--------------------+


Important notes
----------------

StorPerf has added the ability to specify the number of Cinder Volumes per
agent VM to test.  The name of the device that the volume is attached to
has been appended to the host IP address in the metrics so that it can be
tracked independently.

It is now possible to specify custom arguments to FIO.  Different engines
such as libaio, posixaio or psync can be specified, as well as different
mixes for read/write, or any other FIO parameter.


Summary
--------

StorPerf is a standalone framework that uses OpenStack to measure Cinder volume
performance.  If desired, it can push results to the OPNFV Test Results DB, or
the embedded Graphite web interface can be used to perform ad hoc queries.



Release Data
-------------

+--------------------------------------+--------------------------------------+
| **Project**                          | StorPerf                             |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| **Repo/tag**                         | opnfv-7.0.0                          |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| **Release designation**              | Gambia.7                             |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| **Release date**                     | November 9 2018                      |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| **Purpose of the delivery**          |                                      |
|                                      |                                      |
+--------------------------------------+--------------------------------------+

Version change
===============

Module version changes
-----------------------

No changes to any modules.

Reason for version
===================

* Timed release schedule

Features additions
-------------------

* STORPERF-263 Support for multiple jobs
* STORPERF-254 Create new API for Warm Up job
* STORPERF-253 Add uname from each agent to metadata
* STORPERF-250 Update containers to upstream
* STORPERF-246 Add support for custom R/W mix
* STORPERF-239 Add IP addresses of slaves to configurations API
* STORPERF-217 Allow user to specify cinder volume type on stack create
* STORPERF-176 Testing strategy overview document

Bug Fixes
----------

* STORPERF-258 Reporting module does not display any graphs

Deliverables
=============

Software
---------

- `StorPerf master image <https://hub.docker.com/r/opnfv/storperf-master/>`_
  (tag: x86_64-opnfv-7.0.0  or aarch64-opnfv-7.0.0)

- `StorPerf swaggerui <https://hub.docker.com/r/opnfv/storperf-swaggerui/>`_
  (tag: x86_64-opnfv-7.0.0  or aarch64-opnfv-7.0.0)

- `StorPerf graphite image <https://hub.docker.com/r/opnfv/storperf-graphite/>`_
  (tag: x86_64-opnfv-7.0.0  or aarch64-opnfv-7.0.0)

- `StorPerf reporting image <https://hub.docker.com/r/opnfv/storperf-reporting/>`_
  (tag: x86_64-opnfv-7.0.0  or aarch64-opnfv-7.0.0)

- `StorPerf Http-Frontend image <https://hub.docker.com/r/opnfv/storperf-httpfrontend/>`_
  (tag: x86_64-opnfv-7.0.0  or aarch64-opnfv-7.0.0)

Documentation
--------------

- :ref:`User Guide <storperf-userguide>`

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
