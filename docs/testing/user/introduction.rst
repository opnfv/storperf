.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0
.. (c) OPNFV, Dell EMC and others.

=====================
StorPerf Introduction
=====================

The purpose of StorPerf is to provide a tool to measure ephemeral and block
storage performance of OpenStack.

A key challenge to measuring disk performance is to know when the disk (or,
for OpenStack, the virtual disk or volume) is performing at a consistent and
repeatable level of performance.  Initial writes to a volume can perform
poorly due to block allocation, and reads can appear instantaneous when
reading empty blocks.  How do we know when the data reported is valid?  The
Storage Network Industry Association (SNIA_) has developed methods which enable
manufacturers to set, and customers to compare, the performance specifications
of Solid State Storage devices.  StorPerf applies this methodology to OpenStack
Cinder and Glance services to provide a high level of confidence in the
performance metrics in the shortest reasonable time.

.. _SNIA: http://www.snia.org/sites/default/files/HoEasen_SNIA_Solid_State_Storage_Per_Test_1_0.pdf

How Does StorPerf Work?
=======================

Once launched, StorPerf presents you with a ReST interface, along with a
`Swagger UI <https://swagger.io/swagger-ui/>`_ that makes it easier to
form HTTP ReST requests.  Issuing an HTTP POST to the configurations API
causes StorPerf to talk to your OpenStack's heat service to create a new stack
with as many agent VMs and attached Cinder volumes as you specify.

After the stack is created, you can issue one or more jobs by issuing a POST
to the jobs ReST API.  The job is the smallest unit of work that StorPerf
can use to measure the disk's performance.

While the job is running, StorPerf collects the performance metrics from each
of the disks under test every minute.  Once the trend of metrics match the
criteria specified in the SNIA methodology, the job automatically terminates
and the valid set of metrics are available for querying.

What is the criteria?  Simply put, it specifies that when the metrics
measured start to "flat line" and stay within that range for the specified
amount of time, then the metrics are considered to be indicative of a
repeatable level of performance.

What Data Can I Get?
====================

StorPerf provides the following metrics:

* IOPS
* Bandwidth (number of kilobytes read or written per second)
* Latency

These metrics are available for every job, and for the specific workloads,
I/O loads and I/O types (read, write) associated with the job.

As of this time, StorPerf only provides textual reports of the metrics.
