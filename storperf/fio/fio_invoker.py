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
import paramiko


class FIOInvoker(object):

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.event_listeners = set()
        self.event_callback_ids = set()
        self._remote_host = None
        self.callback_id = None

    @property
    def remote_host(self):
        return self._remote_host

    @remote_host.setter
    def remote_host(self, value):
        self._remote_host = value
        self.logger = logging.getLogger(__name__ + ":" + value)

    def register(self, event_listener):
        self.event_listeners.add(event_listener)

    def unregister(self, event_listener):
        self.event_listeners.discard(event_listener)

    def stdout_handler(self, stdout):
        self.logger.debug("Started")
        self.json_body = ""
        try:
            for line in iter(stdout.readline, b''):
                if line.startswith("fio"):
                    line = ""
                    continue
                self.json_body += line
                try:
                    if line == "}\n":
                        json_metric = json.loads(self.json_body)
                        self.json_body = ""

                        for event_listener in self.event_listeners:
                            try:
                                event_listener(self.callback_id, json_metric)
                            except Exception, e:
                                self.logger.exception(
                                    "Notifying listener %s: %s",
                                    self.callback_id, e)
                            self.logger.info(
                                "Event listener callback complete")
                except Exception, e:
                    self.logger.error("Error parsing JSON: %s", e)
        except ValueError:
            pass  # We might have read from the closed socket, ignore it

        stdout.close()
        self.logger.debug("Finished")

    def stderr_handler(self, stderr):
        self.logger.debug("Started")
        for line in iter(stderr.readline, b''):
            self.logger.error("FIO Error: %s", line.rstrip())

        stderr.close()
        self.logger.debug("Finished")

    def execute(self, args=[]):

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(self.remote_host, username='storperf',
                    key_filename='storperf/resources/ssh/storperf_rsa',
                    timeout=2)

        command = "sudo ./fio " + ' '.join(args)
        self.logger.debug("Remote command: %s" % command)
        (_, stdout, stderr) = ssh.exec_command(command)

        tout = Thread(target=self.stdout_handler, args=(stdout,),
                      name="%s stdout" % self._remote_host)
        tout.daemon = True
        tout.start()

        terr = Thread(target=self.stderr_handler, args=(stderr,),
                      name="%s stderr" % self._remote_host)
        terr.daemon = True
        terr.start()

        self.logger.info("Started fio on " + self.remote_host)
        terr.join()
        tout.join()
        self.logger.info("Finished fio on " + self.remote_host)

    def terminate(self):
        self.logger.debug("Terminating fio on " + self.remote_host)
        cmd = ['ssh', '-o', 'StrictHostKeyChecking=no',
               '-o', 'UserKnownHostsFile=/dev/null',
               '-o', 'LogLevel=error',
               '-i', 'storperf/resources/ssh/storperf_rsa',
               'storperf@' + self.remote_host,
               'sudo', 'killall', '-9', 'fio']

        kill_process = subprocess.Popen(cmd,
                                        universal_newlines=True,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)

        for line in iter(kill_process.stdout.readline, b''):
            self.logger.debug("FIO Termination: " + line)

        kill_process.stdout.close()

        for line in iter(kill_process.stderr.readline, b''):
            self.logger.debug("FIO Termination: " + line)

        kill_process.stderr.close()
