##############################################################################
# Copyright (c) 2015 EMC and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

import json
import logging
import subprocess
from threading import Thread


class FIOInvoker(object):

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.event_listeners = set()

    def register(self, event_listener):
        self.event_listeners.add(event_listener)

    def unregister(self, event_listener):
        self.event_listeners.discard(event_listener)

    def stdout_handler(self):
        self.json_body = ""
        try:
            for line in iter(self.fio_process.stdout.readline, b''):
                if line.startswith("fio"):
                    line = ""
                    continue
                self.json_body += line
                try:
                    if line == "}\n":
                        self.logger.debug(
                            "Have a json snippet: %s", self.json_body)
                        json_metric = json.loads(self.json_body)
                        self.json_body = ""

                        for event_listener in self.event_listeners:
                            event_listener(json_metric)

                except Exception, e:
                    self.logger.error("Error parsing JSON: %s", e)
                    pass
        except ValueError:
            pass  # We might have read from the closed socket, ignore it

        self.fio_process.stdout.close()

    def stderr_handler(self):
        for line in iter(self.fio_process.stderr.readline, b''):
            self.logger.error("FIO Error: %s", line)

        self.fio_process.stderr.close()

    def execute(self, args=[]):
        for arg in args:
            self.logger.debug("FIO arg: " + arg)

        self.fio_process = subprocess.Popen(['fio'] + args,
                                            universal_newlines=True,
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE)

        t = Thread(target=self.stdout_handler, args=())
        t.daemon = False
        t.start()

        t = Thread(target=self.stderr_handler, args=())
        t.daemon = False
        t.start()

        t.join()
