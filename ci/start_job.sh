#!/bin/bash -x
##############################################################################
# Copyright (c) 2015 EMC and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

cat << EOF > body.json
{
   "block_sizes": "${BLOCK_SIZE}",
   "nowarm": "string",
   "nossd": "string",
   "deadline": 600,
   "queue_depths": "${QUEUE_DEPTH}",
   "workload": "${WORKLOAD}",
    "metadata": {
       "disk_type": "SSD",
      "pod_name": "${POD_NAME}",
      "scenario_name": "${SCENARIO_NAME}",
      "storage_node_count": ${CINDER_NODES}
   }
}
EOF

curl -s -X POST --header 'Content-Type: application/json' --header 'Accept: application/json' \
    -d @body.json http://127.0.0.1:5000/api/v1.0/jobs