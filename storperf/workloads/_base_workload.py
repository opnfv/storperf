##############################################################################
# Copyright (c) 2015 EMC and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

import logging


class _base_workload(object):

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.default_filesize = "128M"
        self.filename = 'storperf.dat'
        self.options = {
            'ioengine': 'libaio',
            'direct': '1',
            'rw': 'read',
            'bs': '4k',
            'iodepth': '1',
            'numjobs': '1',
            'loops': '2',
            'output-format': 'json',
            'status-interval': '60'
        }
        self.invoker = None

    def execute(self):
        args = []

        if self.filename.startswith("/dev"):
            self.options['size'] = "100%"
            self.logger.debug(
                "Profiling a device, using 100% of " + self.filename)
        else:
            self.options['size'] = self.default_filesize
            self.logger.debug("Profiling a filesystem, using " +
                              self.default_filesize + " file")

        self.options['filename'] = self.filename

        self.setup()

        for key, value in self.options.iteritems():
            args.append('--' + key + "=" + value)

        self.invoker.execute(args)

    def setup(self):
        pass
