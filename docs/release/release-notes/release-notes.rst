.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0

******
Danube
******

This document provides the release notes for Danube of StorPerf.

.. contents::
   :depth: 3
   :local:

Version history
===============

+--------------------+--------------------+--------------------+--------------------+
| **Date**           | **Ver.**           | **Author**         | **Comment**        |
|                    |                    |                    |                    |
+--------------------+--------------------+--------------------+--------------------+
| 2017-05-04         | Danube 2.0         | Mark Beierl        |                    |
|                    |                    |                    |                    |
+--------------------+--------------------+--------------------+--------------------+
| 2017-03-30         | Danube 1.0         | Mark Beierl        |                    |
|                    |                    |                    |                    |
+--------------------+--------------------+--------------------+--------------------+


Summary
=======

StorPerf is a standalone framework that uses OpenStack to measure Cinder volume
performance.  If desired, it can push results to the OPNFV Test Results DB, or
the embedded Graphite web interface can be used to perform ad hoc queries.

Release Data
============

+--------------------------------------+--------------------------------------+
| **Project**                          | StorPerf                             |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| **Repo/commit-ID**                   | storperf/danube.2.0                  |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| **Release designation**              | Danube base release                  |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| **Release date**                     | 2017-05-04                           |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| **Purpose of the delivery**          | OPNFV Danube release 2.0             |
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

None

Bug Fixes
^^^^^^^^^

The following minor bugs have been fixed

* STORPERF-111
* STORPERF-123
* STORPERF-124

See JIRA for full `change log <https://jira.opnfv.org/jira/secure/ReleaseNote.jspa?projectId=11002&version=10713>`_

Deliverables
------------

Software
^^^^^^^^

- `StorPerf Docker image <https://hub.docker.com/r/opnfv/storperf/tags>`_ (tag: danube.2.0)

Documentation
^^^^^^^^^^^^^

- `User Guide <http://docs.opnfv.org/en/stable-danube/submodules/storperf/docs/testing/user/index.html>`_

Known Limitations, Issues and Workarounds
=========================================

Limitations
-----------


Known issues
------------
* STORPERF-56 Cannot delete stack if create failed

Test Result
===========

