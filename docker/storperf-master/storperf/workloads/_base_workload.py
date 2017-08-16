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
        self.logger = logging.getLogger(self.__class__.__name__)
        self.default_filesize = "1G"
        self.filename = '/dev/vdb'
        self.options = {
            'ioengine': 'libaio',
            'direct': '1',
            'rw': 'read',
            'bs': '64k',
            'iodepth': '1',
            'numjobs': '1',
            'loops': '20',
            'output-format': 'json',
            'status-interval': '60'
        }
        self.invoker = None
        self.remote_host = None
        self.id = None

    def execute(self):
        if self.invoker is None:
            raise ValueError("No invoker has been set")

        args = []
        self.invoker.remote_host = self.remote_host
        self.invoker.callback_id = self.fullname

        if self.filename.startswith("/dev"):
            self.options['size'] = "100%"
            self.logger.debug(
                "Profiling a device, using 100% of " + self.filename)
        else:
            self.options['size'] = self.default_filesize
            self.logger.debug("Profiling a filesystem, using "
                              + self.default_filesize + " file")

        self.options['filename'] = self.filename

        self.setup()

        for key, value in self.options.iteritems():
            args.append('--' + key + "=" + value)

        self.invoker.execute(args)

    def terminate(self):
        if self.invoker is not None:
            self.invoker.terminate()

    def setup(self):
        pass

    @property
    def remote_host(self):
        return str(self._remote_host)

    @remote_host.setter
    def remote_host(self, value):
        self._remote_host = value

    @property
    def fullname(self):
        return ("%s.%s.queue-depth.%s.block-size.%s.%s"
                % (str(self.id),
                   self.__class__.__name__,
                   str(self.options['iodepth']),
                   str(self.options['bs']),
                   str(self.remote_host).replace(".", "-")))
