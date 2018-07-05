.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0
.. (c) OPNFV, Dell EMC and others.

=============================
StorPerf Test Execution Guide
=============================

Prerequisites
=============

This guide requires StorPerf to be running and have its ReST API accessible.  If
the ReST API is not running on port 5000, adjust the commands provided here as
needed.

Interacting With StorPerf
=========================

Once the StorPerf container has been started and the ReST API exposed, you can
interact directly with it using the ReST API.  StorPerf comes with a Swagger
interface that is accessible through the exposed port at:

.. code-block:: console

   http://StorPerf:5000/swagger/index.html

The typical test execution follows this pattern:

#. Configure the environment
#. Initialize the cinder volumes
#. Execute one or more performance runs
#. Delete the environment

Configure The Environment
=========================

The following pieces of information are required to prepare the environment:

- The number of VMs/Cinder volumes to create.
- The Cinder volume type (optional) to create
- The Glance image that holds the VM operating system to use.
- The OpenStack flavor to use when creating the VMs.
- The name of the public network that agents will use.
- The size, in gigabytes, of the Cinder volumes to create.
- The number of the Cinder volumes to attach to each VM.
- The availability zone (optional) in which the VM is to be launched. Defaults to **nova**.
- The username (optional) if we specify a custom image.
- The password (optional) for the above image.

**Note**: on ARM based platforms there exists a bug in the kernel which can prevent
VMs from properly attaching Cinder volumes.  There are two known workarounds:

#. Create the environment with 0 Cinder volumes attached, and after the VMs
  have finished booting, modify the stack to have 1 or more Cinder volumes.
  See section on Changing Stack Parameters later in this guide.
#. Add the following image metadata to Glance.  This will cause the Cinder
  volume to be mounted as a SCSI device, and therefore your target will be
  /dev/sdb, etc, instead of /dev/vdb.  You will need to specify this in your
  warm up and workload jobs.

.. code-block:
  --property hw_disk_bus=scsi --property hw_scsi_model=virtio-scsi


The ReST API is a POST to http://StorPerf:5000/api/v1.0/configurations and
takes a JSON payload as follows.

.. code-block:: json

	{
	  "agent_count": int,
	  "agent_flavor": "string",
	  "agent_image": "string",
	  "availability_zone": "string",
	  "password": "string",
	  "public_network": "string",
	  "username": "string",
	  "volume_count": int,
	  "volume_size": int,
	  "volume_type": "string"
	}

This call will block until the stack is created, at which point it will return
the OpenStack heat stack id as well as the IP addresses of the slave agents.

Initialize the Cinder Volumes
=============================
Before executing a test run for the purpose of measuring performance, it is
necessary to fill the Cinder volume with random data.  Failure to execute this
step can result in meaningless numbers, especially for read performance.  Most
Cinder drivers are smart enough to know what blocks contain data, and which do
not.  Uninitialized blocks return "0" immediately without actually reading from
the volume.

Initiating the data fill looks the same as a regular performance test, but uses
the special workload called "_warm_up".  StorPerf will never push _warm_up
data to the OPNFV Test Results DB, nor will it terminate the run on steady state.
It is guaranteed to run to completion, which fills 100% of the volume with
random data.

The ReST API is a POST to http://StorPerf:5000/api/v1.0/jobs and
takes a JSON payload as follows.

.. code-block:: json

   {
      "workload": "_warm_up"
   }

This will return a job ID as follows.

.. code-block:: json

   {
     "job_id": "edafa97e-457e-4d3d-9db4-1d6c0fc03f98"
   }

This job ID can be used to query the state to determine when it has completed.
See the section on querying jobs for more information.

Execute a Performance Run
=========================
Performance runs can execute either a single workload, or iterate over a matrix
of workload types, block sizes and queue depths.

Workload Types
~~~~~~~~~~~~~~
rr
   Read, Random.  100% read of random blocks
rs
   Read, Sequential.  100% read of sequential blocks of data
rw
   Read / Write Mix, Sequential.  70% random read, 30% random write
wr
   Write, Random.  100% write of random blocks
ws
   Write, Sequential.  100% write of sequential blocks.

Custom Workload Types
~~~~~~~~~~~~~~~~~~~~~
New in Gambia (7.0), you can specify custom workload parameters for StorPerf
to pass on to FIO.  This is available in the /api/v2.0/jobs API, and takes
a different format than the default v1.0 API.

The format is as follows:

.. code-block:: json

  "workloads": {
    "name": {
       "fio argument": "fio value"
    }
  }

The name is used the same way the 'rr', 'rs', 'rw', etc is used, but can be
any arbitrary alphanumeric string.  This is for you to identify the job later.
Following the name is a series of arguments to pass on to FIO.  The most
important on of these is the actual I/O operation to perform.  From the `FIO
manual`__, there are a number of different workloads:

.. _FIO_IOP: http://git.kernel.dk/cgit/fio/tree/HOWTO#n985
__ FIO_IOP_

* read
* write
* trim
* randread
* etc

This is an example of how the original 'ws' workload looks in the new format:

.. code-block:: json

  "workloads": {
    "ws": {
       "rw": "write"
    }
  }

Using this format, it is now possible to initiate any combination of IO
workload type.  For example, a mix of 60% reads and 40% writes scattered
randomly throughout the volume being profiled would be:

.. code-block:: json

  "workloads": {
    "6040randrw": {
       "rw": "randrw",
        "rwmixread": "60"
    }
  }

Additional arguments can be added as needed.  Here is an example of random
writes, with 25% duplicated blocks, followed by a second run of 75/25% mixed
reads and writes.  This can be used to test the deduplication capabilities
of the underlying storage driver.

.. code-block:: json

  "workloads": {
    "dupwrite": {
       "rw": "randwrite",
        "dedupe_percentage": "25"
    },
    "7525randrw": {
       "rw": "randrw",
        "rwmixread": "75",
        "dedupe_percentage": "25"
    }
  }

There is no limit on the number of workloads and additional FIO arguments
that can be specified.

Note that as in v1.0, the list of workloads will be iterated over with the
block sizes and queue depths specified.

StorPerf will also do a verification of the arguments given prior to returning
a Job ID from the ReST call.  If an argument fails validation, the error
will be returned in the payload of the response.

Block Sizes
~~~~~~~~~~~
A comma delimited list of the different block sizes to use when reading and
writing data.  Note: Some Cinder drivers (such as Ceph) cannot support block
sizes larger than 16k (16384).

Queue Depths
~~~~~~~~~~~~
A comma delimited list of the different queue depths to use when reading and
writing data.  The queue depth parameter causes FIO to keep this many I/O
requests outstanding at one time.  It is used to simulate traffic patterns
on the system.  For example, a queue depth of 4 would simulate 4 processes
constantly creating I/O requests.

Deadline
~~~~~~~~
The deadline is the maximum amount of time in minutes for a workload to run.  If
steady state has not been reached by the deadline, the workload will terminate
and that particular run will be marked as not having reached steady state.  Any
remaining workloads will continue to execute in order.

.. code-block:: json

   {
      "block_sizes": "2048,16384",
      "deadline": 20,
      "queue_depths": "2,4",
      "workload": "wr,rr,rw"
   }

Metadata
~~~~~~~~
A job can have metadata associated with it for tagging.  The following metadata
is required in order to push results to the OPNFV Test Results DB:

.. code-block:: json

      "metadata": {
          "disk_type": "HDD or SDD",
          "pod_name": "OPNFV Pod Name",
          "scenario_name": string,
          "storage_node_count": int,
          "version": string,
          "build_tag": string,
          "test_case": "snia_steady_state"
      }

Changing Stack Parameters
~~~~~~~~~~~~~~~~~~~~~~~~~
While StorPerf currently does not support changing the parameters of the
stack directly, it is possible to change the stack using the OpenStack client
library.  The following parameters can be changed:

- agent_count: to increase or decrease the number of VMs.
- volume_count: to change the number of Cinder volumes per VM.
- volume_size: to increase the size of each volume.  Note: Cinder cannot shrink volumes.

Increasing the number of agents or volumes, or increasing the size of the volumes
will require you to kick off a new _warm_up job to initialize the newly
allocated volumes.

The following is an example of how to change the stack using the heat client:

.. code-block::
  heat stack-update StorPerfAgentGroup --existing -P "volume_count=2"


Query Jobs Information
======================

By issuing a GET to the job API http://StorPerf:5000/api/v1.0/jobs?job_id=<ID>,
you can fetch information about the job as follows:

- &type=status: to report on the status of the job.
- &type=metrics: to report on the collected metrics.
- &type=metadata: to report back any metadata sent with the job ReST API

Status
~~~~~~
The Status field can be:
- Running to indicate the job is still in progress, or
- Completed to indicate the job is done.  This could be either normal completion
  or manually terminated via HTTP DELETE call.

Workloads can have a value of:
- Pending to indicate the workload has not yet started,
- Running to indicate this is the active workload, or
- Completed to indicate this workload has completed.

This is an example of a type=status call.

.. code-block:: json

   {
     "Status": "Running",
     "TestResultURL": null,
     "Workloads": {
       "eeb2e587-5274-4d2f-ad95-5c85102d055e.ws.queue-depth.1.block-size.16384": "Pending",
       "eeb2e587-5274-4d2f-ad95-5c85102d055e.ws.queue-depth.1.block-size.4096": "Pending",
       "eeb2e587-5274-4d2f-ad95-5c85102d055e.ws.queue-depth.1.block-size.512": "Pending",
       "eeb2e587-5274-4d2f-ad95-5c85102d055e.ws.queue-depth.4.block-size.16384": "Running",
       "eeb2e587-5274-4d2f-ad95-5c85102d055e.ws.queue-depth.4.block-size.4096": "Pending",
       "eeb2e587-5274-4d2f-ad95-5c85102d055e.ws.queue-depth.4.block-size.512": "Pending",
       "eeb2e587-5274-4d2f-ad95-5c85102d055e.ws.queue-depth.8.block-size.16384": "Completed",
       "eeb2e587-5274-4d2f-ad95-5c85102d055e.ws.queue-depth.8.block-size.4096": "Pending",
       "eeb2e587-5274-4d2f-ad95-5c85102d055e.ws.queue-depth.8.block-size.512": "Pending"
     }
   }

If the `job_id` is not provided along with `type` status, then all jobs are returned along with their status.
Metrics
~~~~~~~
Metrics can be queried at any time during or after the completion of a run.
Note that the metrics show up only after the first interval has passed, and
are subject to change until the job completes.

This is a sample of a type=metrics call.

.. code-block:: json

   {
     "rw.queue-depth.1.block-size.512.read.bw": 52.8,
     "rw.queue-depth.1.block-size.512.read.iops": 106.76199999999999,
     "rw.queue-depth.1.block-size.512.read.lat_ns.mean": 93.176,
     "rw.queue-depth.1.block-size.512.write.bw": 22.5,
     "rw.queue-depth.1.block-size.512.write.iops": 45.760000000000005,
     "rw.queue-depth.1.block-size.512.write.lat_ns.mean": 21764.184999999998
   }

Abort a Job
===========
Issuing an HTTP DELETE to the job api http://StorPerf:5000/api/v1.0/jobs will
force the termination of the whole job, regardless of how many workloads
remain to be executed.

.. code-block:: bash

  curl -X DELETE --header 'Accept: application/json' http://StorPerf:5000/api/v1.0/jobs

List all Jobs
=============
A list of all Jobs can also be queried. You just need to issue a GET request without any
Job ID.

.. code-block:: bash

  curl -X GET --header 'Accept: application/json' http://StorPerf/api/v1.0/jobs

Delete the Environment
======================
After you are done testing, you can have StorPerf delete the Heat stack by
issuing an HTTP DELETE to the configurations API.

.. code-block:: bash

  curl -X DELETE --header 'Accept: application/json' http://StorPerf:5000/api/v1.0/configurations

You may also want to delete an environment, and then create a new one with a
different number of VMs/Cinder volumes to test the impact of the number of VMs
in your environment.

Viewing StorPerf Logs
=====================

Logs are an integral part of any application as they help debugging the application. The user just
needs to issue an HTTP request. To view the entire logs

.. code-block:: bash

  curl -X GET --header 'Accept: application/json' http://StorPerf:5000/api/v1.0/logs?lines=all

Alternatively, one can also view a certain amount of lines by specifying the number in the
request. If no lines are specified, then last 35 lines are returned

.. code-block:: bash

  curl -X GET --header 'Accept: application/json' http://StorPerf:5000/api/v1.0/logs?lines=12
