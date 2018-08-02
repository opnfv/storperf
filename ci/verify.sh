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
pip install autoflake==1.2
pip install autopep8==1.3.5
pip install coverage==4.5.1
#pip install cryptography
pip install flake8==3.5.0
pip install mock==2.0.0
pip install nose==1.3.7
pip install -r docker/storperf-master/requirements.pip

final_rc=0

flake8 docker/storperf-*
flake8rc=$?

for testdir in docker/storperf-*
do
    if [ -d $testdir/tests ]
    then
        cwd=$(pwd)
        cd $testdir

        nosetests --with-xunit \
                 --with-coverage \
                 --cover-package=storperf\
                 --cover-xml \
                 --cover-html \
                 tests
        rc=$?
        if [ $rc -ne 0 ]
        then
            final_rc=$rc
        fi
        cd $cwd
    fi
done

cp ./docker/storperf-master/coverage.xml .
cp ./docker/storperf-master/nosetests.xml .

deactivate

if [ $flake8rc -ne 0 ]
then
    echo "Formatting did not meet guidelines"
    exit $flake8rc
fi

exit $final_rc
