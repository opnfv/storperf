.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0


This document provides the release notes for Hunter 1.0 of StorPerf.

.. contents::
   :depth: 3
   :local:


Version history
===============


+--------------------+--------------------+--------------------+--------------------+
| **Date**           | **Ver.**           | **Author**         | **Comment**        |
|                    |                    |                    |                    |
+--------------------+--------------------+--------------------+--------------------+
| 2018-11-09         | Hunter 1.0         | Mark Beierl        |                    |
|                    |                    |                    |                    |
+--------------------+--------------------+--------------------+--------------------+


Important notes
----------------

It is now possible to specify arbitrary IP addresses to StorPerf and not
require OpenStack or Heat for stack creation.

Summary
--------

StorPerf is a standalone framework that uses OpenStack to measure Cinder volume
performance.  If desired, it can push results to the OPNFV Test Results DB, or
the embedded Graphite web interface can be used to perform ad hoc queries.

This release provides the ability to use existing servers (virtual or physical)
as the targets for workload execution.  All that is required is the IP address
and the SSH key or username/password for StorPerf to be able to log in and
start FIO workloads.

Release Data
-------------

+--------------------------------------+--------------------------------------+
| **Project**                          | StorPerf                             |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| **Repo/tag**                         | opnfv-8.0.0                          |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| **Release designation**              | Hunter.8                             |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| **Release date**                     | May 10, 2019                         |
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

* STORPERF-265 Add support for stackless (IP address) runs
* STORPERF-228 Allow user to specify list of IP addresses for StorPerf test

Bug Fixes
----------

None

Deliverables
=============

Software
---------

- `StorPerf master image <https://hub.docker.com/r/opnfv/storperf-master/>`_
  (tag: x86_64-opnfv-8.0.0  or aarch64-opnfv-8.0.0)

- `StorPerf swaggerui <https://hub.docker.com/r/opnfv/storperf-swaggerui/>`_
  (tag: x86_64-opnfv-8.0.0  or aarch64-opnfv-8.0.0)

- `StorPerf graphite image <https://hub.docker.com/r/opnfv/storperf-graphite/>`_
  (tag: x86_64-opnfv-8.0.0  or aarch64-opnfv-8.0.0)

- `StorPerf reporting image <https://hub.docker.com/r/opnfv/storperf-reporting/>`_
  (tag: x86_64-opnfv-8.0.0  or aarch64-opnfv-8.0.0)

- `StorPerf Http-Frontend image <https://hub.docker.com/r/opnfv/storperf-httpfrontend/>`_
  (tag: x86_64-opnfv-8.0.0  or aarch64-opnfv-8.0.0)

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


