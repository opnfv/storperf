##############################################################################
# Copyright (c) 2016 Dell EMC and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
"""
Creates a gate object that allows synchronization between an arbitrary
number of callers.
"""
import logging
import time
from threading import Lock


class FailureToReportException(Exception):
    pass


class ThreadGate(object):

    def __init__(self, size, timeout=60):
        self.logger = logging.getLogger(__name__)
        self._gate_size = size
        self._timeout = timeout
        self._registrants = {}
        self._creation_time = time.time()
        self._lock = Lock()

    """
    Calling this method returns a true or false, indicating that enough
    of the other registrants have reported in
    """

    def report(self, gate_id):
        with self._lock:
            now = time.time()
            self._registrants[gate_id] = now
            ready = True
            self.logger.debug("Gate report for %s", gate_id)

            total_missing = self._gate_size - len(self._registrants)
            if total_missing > 0:
                self.logger.debug("Not all registrants have reported in")
                time_since_creation = now - self._creation_time
                if (time_since_creation > (self._timeout * 2)):
                    self.logger.error(
                        "%s registrant(s) have never reported in",
                        total_missing)
                    raise FailureToReportException
                return False

            for k, v in self._registrants.items():
                time_since_last_report = now - v
                self.logger.info("Type of time_since = " +
                                 str(type(time_since_last_report)))
                if time_since_last_report > self._timeout:
                    self.logger.debug("Registrant %s last reported %s ago",
                                      k, time_since_last_report)
                    ready = False

            self.logger.debug("Gate pass? %s", ready)

            if ready:
                self._registrants.clear()

            return ready
