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

pip install setuptools
pip install autoflake=00.6.6
pip install autopep8==1.2.2
pip install coverage==4.0.3
pip install flask==0.10
pip install flask-restful==0.3.5
pip install funcsigs==0.4
pip install flake8==2.5.4
pip install html2text==2016.1.8
pip install mock==1.3.0
pip install nose==1.3.7
pip install pysqlite==2.8.2
pip install python-cinderclient==1.6.0
pip install python-glanceclient==1.1.0
pip install python-heatclient==0.8.0
pip install python-keystoneclient==1.6.0
pip install python-neutronclient==2.6.0
pip install python-novaclient==2.28.1
pip install pyyaml==3.10
pip install requests==2.9.1
pip install six==1.10.0

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