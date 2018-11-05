##############################################################################
# Copyright (c) 2015 EMC and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

import logging
from storperf.workloads import _base_workload


class _custom_workload(_base_workload._base_workload):

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.default_filesize = "1G"
        self.filename = '/dev/vdb'
        self.fixed_options = {
            'output-format': 'json',
            'status-interval': '60'
        }
        self.options = {
            'ioengine': 'libaio',
            'loops': '200',
            'direct': '1',
            'numjobs': '1',
            'rw': 'read',
            'bs': '64k',
            'iodepth': '1'
        }
        self.options.update(self.fixed_options)
        self.invoker = None
        self.remote_host = None
        self.id = None
