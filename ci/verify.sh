#!/bin/bash
##############################################################################
# Copyright (c) 2015 EMC and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

echo "Verifying code format and compliance..."

if [ -z $WORKSPACE ]
then
    WORKSPACE="$HOME"
fi

virtualenv $WORKSPACE/storperf_venv
source $WORKSPACE/storperf_venv/bin/activate

pip install --upgrade setuptools
pip install coverage==4.0.3
pip install flake8==2.5.4
pip install funcsigs==0.4
pip install mock==1.3.0
pip install nose==1.3.7

python ci/setup.py develop

flake8 storperf

nosetests --with-xunit \
         --with-coverage \
         --cover-package=storperf\
         --cover-xml \
         storperf
rc=$?

deactivate

exit $rc