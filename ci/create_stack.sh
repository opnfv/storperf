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
  "agent_count": $1,
  "agent_image": "Trusty x86_64",
  "public_network": "ext-net",
  "volume_size": $2
}
EOF

curl -X POST --header 'Content-Type: application/json' \
     --header 'Accept: application/json' -d @body.json \
     'http://127.0.0.1:5000/api/v1.0/configurations'

