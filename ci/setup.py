##############################################################################
# Copyright (c) 2015 EMC and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

from setuptools import setup, find_packages


setup(
    name="storperf",
    version="0.dev0",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'storperf': [
            'storperf/resources/hot/*'
        ]
    },
    url="https://www.opnfv.org",
    install_requires=["flask==0.10",
                      "flask-restful==0.3.5",
                      "flask-restful-swagger==0.19",
                      "html2text==2016.1.8",
                      "python-cinderclient==1.6.0",
                      "python-glanceclient==1.1.0",
                      "python-heatclient==0.8.0",
                      "python-keystoneclient==1.6.0",
                      "python-neutronclient==2.6.0",
                      "python-novaclient==2.28.1",
                      "pyyaml==3.10",
                      "requests==2.13.0",
                      "six==1.10.0"
                      ],
    entry_points={
        'console_scripts': [
            'storperf=storperf.main:main',
        ],
    }
)
