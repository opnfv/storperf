.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0


This document provides the release notes for Danube 3.0 of StorPerf.

.. contents::
   :depth: 3
   :local:


Version history
---------------

+--------------------+--------------------+--------------------+--------------------+
| **Date**           | **Ver.**           | **Author**         | **Comment**        |
|                    |                    |                    |                    |
+--------------------+--------------------+--------------------+--------------------+
| 2017-07-14         | Danube 3.0         | Mark Beierl        |                    |
|                    |                    |                    |                    |
+--------------------+--------------------+--------------------+--------------------+
| 2017-05-04         | Danube 2.0         | Mark Beierl        |                    |
|                    |                    |                    |                    |
+--------------------+--------------------+--------------------+--------------------+
| 2017-03-30         | Danube 1.0         | Mark Beierl        |                    |
|                    |                    |                    |                    |
+--------------------+--------------------+--------------------+--------------------+


Important notes
===============
This is the last release where StorPerf is delivered as a single container.  Moving
forward, StorPerf must be run using docker-compose.

Summary
=======

StorPerf is a standalone framework that uses OpenStack to measure Cinder volume
performance.  If desired, it can push results to the OPNFV Test Results DB, or
the embedded Graphite web interface can be used to perform ad hoc queries.

This release supports Keystone v3 authentication

Release Data
============

+--------------------------------------+--------------------------------------+
| **Project**                          | StorPerf                             |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| **Repo/commit-ID**                   | storperf/danube.3.0                  |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| **Release designation**              | Danube base release                  |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| **Release date**                     | 2017-07-14                           |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| **Purpose of the delivery**          | OPNFV Danube release 3.0             |
|                                      |                                      |
+--------------------------------------+--------------------------------------+

Version change
--------------

Module version changes
^^^^^^^^^^^^^^^^^^^^^^

No changes to any modules.

Reason for version
------------------

Features additions
^^^^^^^^^^^^^^^^^^

* STORPERF-139 - Expose maximum number of steady state samples as a parameter

Bug Fixes
^^^^^^^^^

The following minor bugs have been fixed

* STORPERF-127 - Unable to communicate using v3 authentication due to missing domain.
* STORPERF-128 - Daily Danube job uses latest tag from docker
* STORPERF-153 - Profiling a file does not work
* STORPERF-154 - PROJECT_DOMAIN_ID not recognized

See JIRA for full `change log <https://jira.opnfv.org/jira/secure/ReleaseNote.jspa?projectId=11002&version=10714>`_

Deliverables
------------

Software
^^^^^^^^

- `StorPerf Docker image <https://hub.docker.com/r/opnfv/storperf/tags>`_ (tag: danube.3.0)

Documentation
^^^^^^^^^^^^^

- `User Guide <http://docs.opnfv.org/en/stable-danube/submodules/storperf/docs/testing/user/index.html>`_

Known Limitations, Issues and Workarounds
=========================================

Limitations
-----------


Known issues
------------
* STORPERF-56 - Cannot delete stack if create failed
* STORPERF-180 - No details if stack create failed

Test Result
===========

