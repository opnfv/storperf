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
            'loops': '200',
            'output-format': 'json',
            'status-interval': '60'
        }
        self.invoker = None
        self.remote_host = None
        self.id = None
        self.name = self.__class__.__name__

    def execute(self, parse_only=False):
        if self.invoker is None:
            raise ValueError("No invoker has been set")

        args = []
        self.invoker.remote_host = self.remote_host
        self.invoker.callback_id = self.fullname

        if self.filename.startswith("/dev"):
            self.options['size'] = "100%"
            self.logger.debug(
                "Profiling a device, using 100% of " + self.filename)
            self.options['filename'] = self.filename
        else:
            if 'size' not in self.options:
                self.options['size'] = self.default_filesize
            self.logger.debug("Profiling a filesystem, using " +
                              self.options['size'] + " file")
            if not self.filename.endswith('/'):
                self.filename = self.filename + "/"
            self.options['directory'] = self.filename
            self.options['filename_format'] = "'storperf.$jobnum.$filenum'"

        self.setup()

        for key, value in self.options.items():
            if value is not None:
                args.append('--' + key + "=" + str(value))
            else:
                args.append('--' + key)

        if parse_only:
            args.append('--parse-only')

        return self.invoker.execute(args)

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
        host_file = self.remote_host + "." + self.filename
        host_file = host_file.replace(".", "-").replace("/", "-")
        return ("%s.%s.queue-depth.%s.block-size.%s.%s"
                % (str(self.id),
                   self.name,
                   str(self.options['iodepth']),
                   str(self.options['bs']),
                   host_file))
