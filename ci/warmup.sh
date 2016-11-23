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
   "block_sizes": "16384",
   "nowarm": "string",
   "nossd": "string",
   "queue_depths": "8",
   "workload": "_warm_up",
   "metadata": {
      "disk_type": "SSD",
      "pod_name": "intel-pod9",
      "scenario_name": "$1_warm_up",
      "storage_node_count": "$2"
   }
}
EOF

curl -s -X POST --header 'Content-Type: application/json' --header 'Accept: application/json' \
    -d @body.json http://127.0.0.1:5000/api/v1.0/jobs
