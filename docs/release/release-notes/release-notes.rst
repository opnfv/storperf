.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0


This document provides the release notes for Euphrates 3.0 of StorPerf.

.. contents::
   :depth: 3
   :local:


Version history
===============


+--------------------+--------------------+--------------------+--------------------+
| **Date**           | **Ver.**           | **Author**         | **Comment**        |
|                    |                    |                    |                    |
+--------------------+--------------------+--------------------+--------------------+
| 2017-10-06         | Euphrates 1.0      | Mark Beierl        |                    |
|                    |                    |                    |                    |
+--------------------+--------------------+--------------------+--------------------+


Important notes
----------------

This is the release where StorPerf is not delivered as a single container but
is delivered as a series of networked containers. StorPerf must be run using
docker-compose.

Summary
--------

StorPerf is a standalone framework that uses OpenStack to measure Cinder volume
performance.  If desired, it can push results to the OPNFV Test Results DB, or
the embedded Graphite web interface can be used to perform ad hoc queries.

This release changes to docker-compose framework and adds the StorPerf
reporting module.  It also marks a change from microsecond (us) to
nano-second precision for all reported latencies.  This is denoted by a change
from lat.mean to lat_ns.mean for read and write metrics.

Release Data
-------------

+--------------------------------------+--------------------------------------+
| **Project**                          | StorPerf                             |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| **Repo/commit-ID**                   | storperf/euphrates.1.0               |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| **Release designation**              | Euphrates base release               |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| **Release date**                     | 2017-10-06                           |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| **Purpose of the delivery**          | OPNFV Euphrates release 1.0          |
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

* STORPERF-125 - StorPerf container decomposition
* STORPERF-141 - Create a series of graphs to support SNIA targers

Bug Fixes
----------

The following minor bugs have been fixed


See JIRA for full `change log <https://jira.opnfv.org/jira/secure/ReleaseNote.jspa?projectId=11002&version=10714>`_

Deliverables
=============

Software
---------

- `StorPerf master image <https://hub.docker.com/r/opnfv/storperf-master/>`_ (tag: euphrates.1.0)

- `StorPerf swaggerui <https://hub.docker.com/r/opnfv/storperf-swaggerui/>`_ (tag: euphrates.1.0)

- `StorPerf graphite image <https://hub.docker.com/r/opnfv/storperf-graphite/>`_ (tag: euphrates.1.0)

- `StorPerf reporting image <https://hub.docker.com/r/opnfv/storperf-reporting/>`_ (tag: euphrates.1.0)

- `StorPerf Http-Frontend image <https://hub.docker.com/r/opnfv/storperf-httpfrontend/>`_ (tag: euphrates.1.0)

Documentation
--------------

- `User Guide <http://docs.opnfv.org/en/latest/submodules/storperf/docs/testing/user/index.html>`_

Known Limitations, Issues and Workarounds
------------------------------------------

Limitations
============

* Does not work with a target OS that requires authentication instead of using init-cloud for generating the ssh key.

Known issues
=============
* STORPERF-56 - Cannot delete stack if create failed

Test Result
===========

