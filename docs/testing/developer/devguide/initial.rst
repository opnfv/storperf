.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0
.. (c) OPNFV, Dell EMC and others.

================
Initial Set up
================

Getting the Code
================

Replace your LFID with your actual Linux Foundation ID.

.. code-block:: bash

    git clone ssh://YourLFID@gerrit.opnfv.org:29418/storperf


Virtual Environment
=======================
It is preferred to use virtualenv for Python dependencies. This way it is known
exactly what libraries are needed, and can restart from a clean state at any
time to ensure any library is not missing.  Simply running the script:

.. code-block:: bash

    ci/verify.sh

from inside the storperf directory will automatically create a virtualenv in
the home directory called 'storperf_venv'. This will be used as the Python
interpreter for the IDE.


Docker Version
=======================
In order to run the full set of StorPerf services, docker and docker-compose
are required to be installed. This requires docker 17.05 at a minimum.

.. code-block:: bash

    https://docs.docker.com/engine/installation/linux/docker-ce/ubuntu/

