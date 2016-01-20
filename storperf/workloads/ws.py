##############################################################################
# Copyright (c) 2015 EMC and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
from storperf.workloads import _base_workload


class ws(_base_workload._base_workload):

    def setup(self):
        self.options['name'] = 'sequential_write'
        self.options['rw'] = 'write'
