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
from threading import Thread
import paramiko
from storperf.utilities import ip_helper


class FIOInvoker(object):

    def __init__(self, var_dict={}):
        self.logger = logging.getLogger(__name__)
        self.event_listeners = set()
        self.event_callback_ids = set()
        self._remote_host = None
        self.callback_id = None
        self.terminated = False
        self.metadata = var_dict
        self.stderr = []

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
                if type(line) == bytes:
                    line = line.decode('utf=8')
                if line.startswith("fio"):
                    line = ""
                    continue
                self.json_body += line
                try:
                    if line == "}\n":
                        json_metric = json.loads(self.json_body)
                        self.json_body = ""

                        if not self.terminated:
                            for event_listener in self.event_listeners:
                                try:
                                    self.logger.debug(
                                        "Event listener callback")
                                    event_listener(
                                        self.callback_id, json_metric)
                                except Exception as e:
                                    self.logger.exception(
                                        "Notifying listener %s: %s",
                                        self.callback_id, e)
                                self.logger.debug(
                                    "Event listener callback complete")
                except Exception as e:
                    self.logger.error("Error parsing JSON: %s", e)
        except IOError:
            pass  # We might have read from the closed socket, ignore it

        stdout.close()
        self.logger.debug("Finished")

    def stderr_handler(self, stderr):
        self.logger.debug("Started")
        for line in iter(stderr.readline, b''):
            if len(line) > 0:
                self.logger.error("FIO Error: %s", line.rstrip())
            self.stderr.append(line.rstrip())

            # Sometime, FIO gets stuck and will give us this message:
            # fio: job 'sequential_read' hasn't exited in 60 seconds,
            # it appears to be stuck. Doing forceful exit of this job.
            # A second killall of fio will release it stuck process.

            if 'it appears to be stuck' in line:
                self.terminate()

        stderr.close()
        self.logger.debug("Finished")

    def execute(self, args=[]):
        ssh = self._ssh_client()

        command = "sudo ./fio " + ' '.join(args)
        self.logger.debug("Remote command: %s" % command)

        chan = ssh.get_transport().open_session(timeout=None)
        chan.settimeout(None)
        chan.exec_command(command)
        stdout = chan.makefile('r', -1)
        stderr = chan.makefile_stderr('r', -1)

        tout = Thread(target=self.stdout_handler, args=(stdout,),
                      name="%s stdout" % self._remote_host)
        tout.daemon = True
        tout.start()

        terr = Thread(target=self.stderr_handler, args=(stderr,),
                      name="%s stderr" % self._remote_host)
        terr.daemon = True
        terr.start()

        self.logger.info("Started fio on " + self.remote_host)
        exit_status = chan.recv_exit_status()
        self.logger.info("Finished fio on %s with exit code %s" %
                         (self.remote_host, exit_status))

        stdout.close()
        stderr.close()

        self.logger.debug("Joining stderr handler")
        terr.join()
        self.logger.debug("Joining stdout handler")
        tout.join()
        self.logger.debug("Ended")
        if exit_status != 0:
            return self.stderr
        return None

    def terminate(self):
        self.logger.debug("Terminating fio on " + self.remote_host)
        self.terminated = True

        ssh = self._ssh_client()

        kill_commands = ['sudo killall fio',
                         'sudo pkill fio']
        for command in kill_commands:
            self.logger.debug("Executing on %s: %s" %
                              (self.remote_host, command))
            (_, stdout, stderr) = ssh.exec_command(command)

        for line in stdout.readlines():
            self.logger.debug(line.strip())
        for line in stderr.readlines():
            self.logger.error(line.strip())

        stdout.close()
        stderr.close()

    def _ssh_client(self):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        address, port = ip_helper.parse_address_and_port(self.remote_host)
        if 'username' in self.metadata and 'password' in self.metadata:
            ssh.connect(address,
                        port=port,
                        username=self.metadata['username'],
                        password=self.metadata['password'],
                        timeout=5)
            return ssh
        elif 'username' in self.metadata and 'ssh_key' in self.metadata:
            ssh.connect(address,
                        port=port,
                        username=self.metadata['username'],
                        pkey=self.metadata['ssh_key'],
                        timeout=5)
            return ssh
        else:
            ssh.connect(address,
                        port=port,
                        username='storperf',
                        key_filename='storperf/resources/ssh/storperf_rsa',
                        timeout=5)
            return ssh
