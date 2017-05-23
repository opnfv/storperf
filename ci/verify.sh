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

pip install --upgrade setuptools==33.1.1
pip install autoflake==0.6.6
pip install autopep8==1.2.2
pip install coverage==4.1
pip install flask==0.10
pip install flask-restful==0.3.5
pip install flask-restful-swagger==0.19
pip install flask-swagger==0.2.12
pip install funcsigs==0.4
pip install flake8==2.5.4
pip install html2text==2016.1.8
pip install keystoneauth1==2.12.1
pip install numpy==1.6
pip install matplotlib==1.3.1
pip install mock==1.3.0
pip install nose==1.3.7
pip install paramiko==2.0.2
pip install python-cinderclient==1.6.0
pip install python-glanceclient==1.1.0
pip install python-heatclient==0.8.0
pip install python-keystoneclient==1.6.0
pip install python-neutronclient==2.6.0
pip install python-novaclient==2.28.1
pip install pyyaml==3.10
pip install requests==2.13.0
pip install scp==0.10.2
pip install six==1.10.0

python ci/setup.py develop

flake8 storperf

flake8rc=$?

nosetests --with-xunit \
         --with-coverage \
         --cover-package=storperf\
         --cover-xml \
         --cover-html \
         tests
rc=$?

deactivate

if [ $flake8rc -ne 0 ]
then
    echo "Formatting did not meet guidelines"
    exit $flake8rc
fi

exit $rc
