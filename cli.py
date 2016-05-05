##############################################################################
# Copyright (c) 2015 EMC and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
"""
"""

from storperf.storperf_master import StorPerfMaster
from threading import Thread
import cPickle
import getopt
import json
import logging
import logging.config
import logging.handlers
import socket
import struct
import sys

import requests


class Usage(Exception):
    pass


def event(event_string):
    logging.getLogger(__name__).info(event_string)


class LogRecordStreamHandler(object):

    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((
            'localhost', logging.handlers.DEFAULT_UDP_LOGGING_PORT))
        self.level = logging.INFO

    def read_logs(self):
        try:
            while True:
                datagram = self.socket.recv(8192)
                chunk = datagram[0:4]
                struct.unpack(">L", chunk)[0]
                chunk = datagram[4:]
                obj = cPickle.loads(chunk)
                record = logging.makeLogRecord(obj)
                if (record.levelno >= self.level):
                    logger = logging.getLogger(record.name)
                    logger.handle(record)

        except Exception as e:
            print "ERROR: " + str(e)
        finally:
            self.socket.close()


def main(argv=None):
    verbose = False
    debug = False
    report = None
    erase = False
    terminate = False
    options = {}

    storperf = StorPerfMaster()

    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "t:w:r:f:escvdTh",
                                       ["target=",
                                        "workload=",
                                        "report=",
                                        "configure=",
                                        "erase",
                                        "nossd",
                                        "nowarm",
                                        "verbose",
                                        "debug",
                                        "terminate",
                                        "help",
                                        ])
        except getopt.error, msg:
            raise Usage(msg)

        configuration = None
        options['workload'] = None

        for o, a in opts:
            if o in ("-h", "--help"):
                print __doc__
                return 0
            elif o in ("-t", "--target"):
                options['filename'] = a
            elif o in ("-v", "--verbose"):
                verbose = True
            elif o in ("-d", "--debug"):
                debug = True
            elif o in ("-s", "--nossd"):
                options['nossd'] = a
            elif o in ("-c", "--nowarm"):
                options['nowarm'] = False
            elif o in ("-w", "--workload"):
                options['workload'] = a
            elif o in ("-r", "--report"):
                report = a
            elif o in ("-e", "--erase"):
                erase = True
            elif o in ("-T", "--terminate"):
                terminate = True
            elif o in ("-f", "--configure"):
                configuration = dict(x.split('=') for x in a.split(','))

        if (debug) or (verbose):
            udpserver = LogRecordStreamHandler()

            if (debug):
                udpserver.level = logging.DEBUG

            logging.basicConfig(format="%(asctime)s - %(name)s - " +
                                "%(levelname)s - %(message)s")

            t = Thread(target=udpserver.read_logs, args=())
            t.setDaemon(True)
            t.start()

        if (erase):
            response = requests.delete(
                'http://127.0.0.1:5000/api/v1.0/configure')
            if (response.status_code == 400):
                content = json.loads(response.content)
                raise Usage(content['message'])
            return 0

        if (terminate):
            response = requests.delete(
                'http://127.0.0.1:5000/api/v1.0/job')
            if (response.status_code == 400):
                content = json.loads(response.content)
                raise Usage(content['message'])
            return 0

        if (configuration is not None):
            response = requests.post(
                'http://127.0.0.1:5000/api/v1.0/configure', json=configuration)
            if (response.status_code == 400):
                content = json.loads(response.content)
                raise Usage(content['message'])

        if (report is not None):
            print storperf.fetch_results(report)
        else:
            print "Calling start..."
            response = requests.post(
                'http://127.0.0.1:5000/api/v1.0/job', json=options)
            if (response.status_code == 400):
                content = json.loads(response.content)
                raise Usage(content['message'])

            content = json.loads(response.content)
            print "Started job id: " + content['job_id']

    except Usage as e:
        print >> sys.stderr, str(e)
        print >> sys.stderr, "For help use --help"
        return 2

    except Exception as e:
        print >> sys.stderr, str(e)
        return 2


if __name__ == "__main__":
    sys.exit(main())
