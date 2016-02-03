#!/bin/bash
##############################################################################
# Copyright (c) 2015 EMC and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

if [ -z $WORKSPACE ]
then
    WORKSPACE="$HOME"
fi

virtualenv $WORKSPACE/storperf_venv
source $WORKSPACE/storperf_venv/bin/activate

pip install --upgrade setuptools
pip install nose -I
pip install coverage -I
python ci/setup.py develop


if [ -x /usr/bin/flake8 ]; then
    flake8 storperf
fi

nosetests --with-xunit \
         --with-coverage \
         --cover-package=storperf\
         --cover-xml \
         storperf

deactivate