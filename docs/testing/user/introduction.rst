.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0
.. (c) OPNFV, Dell EMC and others.

==================================
StorPerf Container Execution Guide
==================================

Planning
========

There are some ports that the container can expose:

    * Deprecated: 22 for SSHD. Username and password are root/storperf. This is used for CLI access only
    * 5000 for StorPerf ReST API.
    * 8000 for StorPerf's Graphite Web Server

OpenStack Credentials
~~~~~~~~~~~~~~~~~~~~~

You must have your OpenStack Controller environment variables defined and passed to
the StorPerf container. The easiest way to do this is to put the rc file contents
into a clean file called admin.rc that looks similar to this for V2 authentication:

.. code-block:: console

    OS_AUTH_URL=http://10.13.182.243:5000/v2.0
    OS_TENANT_ID=e8e64985506a4a508957f931d1800aa9
    OS_TENANT_NAME=admin
    OS_PROJECT_NAME=admin
    OS_USERNAME=admin
    OS_PASSWORD=admin
    OS_REGION_NAME=RegionOne

For V3 authentication, at a minimum, use the following:

.. code-block:: console

   OS_AUTH_URL=http://10.10.243.14:5000/v3
   OS_USERNAME=admin
   OS_PASSWORD=admin
   OS_PROJECT_DOMAIN_NAME=Default
   OS_PROJECT_NAME=admin
   OS_USER_DOMAIN_NAME=Default


Additionally, if you want your results published to the common OPNFV Test Results
DB, add the following:

.. code-block:: console

    TEST_DB_URL=http://testresults.opnfv.org/testapi

Running StorPerf Container
==========================

As of Euphrates (development) release (June 2017), StorPerf has changed to use
docker-compose in order to start its services.  Two files are needed in order
to start StorPerf:

#. docker-compose.yaml
#. nginx.conf

Copy and paste the following into a terminal to create the docker-compose.yaml

.. code-block:: console

    cat << EOF > docker-compose.yaml
    version: '2'
    services:
        storperf:
            container_name: "storperf"
            image: "opnfv/storperf:${TAG}"
            ports:
                - "8000:8000"
            env_file: ${ENV_FILE}
            volumes:
                - ${CARBON_DIR}:/opt/graphite/storage/whisper
        swagger-ui:
            container_name: "swagger-ui"
            image: "schickling/swagger-ui"
        http-front-end:
            container_name: "http-front-end"
            image: nginx:stable-alpine
            ports:
                - "5000:5000"
            volumes:
                - ./nginx.conf:/etc/nginx/nginx.conf:ro
            links:
                - storperf
                - swagger-ui
    EOF

Copy and paste the following into a terminal to create the nginx.conf

.. code-block:: console

    cat << EOF > nginx.conf
    http {
        include            mime.types;
        default_type       application/octet-stream;
        sendfile           on;
        keepalive_timeout  65;
        map $args $containsurl {
            default 0;
            "~(^|&)url=[^&]+($|&)" 1;
        }
        server {
            listen 5000;
            location /api/ {
                proxy_pass http://storperf:5000;
                proxy_set_header Host $host:$proxy_port;
            }
            location /swagger/ {
                if ($containsurl = 0) {
                    return 302 $scheme://$host:$server_port$uri?url=http://$host:$server_port/api/spec.json$args;
                }
                proxy_pass http://swagger-ui:80/;
            }
        }
    }
    events {
        worker_connections 1024;
    }

    EOF

Local disk used for the Carbon DB storage as the default size of the docker
container is only 10g. Here is an example of how to create a local storage
directory and set its permissions so that StorPerf can write to it:

.. code-block:: console

    mkdir -p ./carbon
    sudo chown 33:33 ./carbon


The following command will start all the StorPerf services:

.. code-block:: console

    TAG=latest ENV_FILE=./admin.rc CARBON_DIR=./carbon/ docker-compose up -d

You can now view the StorPerf SwaggerUI at:

``http://127.0.0.1:5000/swagger``


Docker Exec
~~~~~~~~~~~

If needed, the container can be entered with docker exec.  This is not normally
required.

.. code-block:: console

    docker exec -it storperf bash
