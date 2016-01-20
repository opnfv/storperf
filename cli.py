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
from storperf.test_executor import UnknownWorkload
import getopt
import json
import logging.config
import os
import sys
import time

import requests

import html2text


class Usage(Exception):

    def __init__(self, msg):
        self.msg = msg


def setup_logging(
    default_path='storperf/logging.json',
    default_level=logging.INFO,
    env_key='LOG_CFG'
):
    """Setup logging configuration
    """

    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)


def event(event_string):
    logging.getLogger(__name__).info(event_string)


def main(argv=None):
    setup_logging()
    verbose = False
    debug = False
    workloads = None
    report = None
    erase = False

    storperf = StorPerfMaster()

    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "t:w:r:f:escvdh",
                                       ["target=",
                                        "workload=",
                                        "report=",
                                        "configure=",
                                        "erase",
                                        "nossd",
                                        "nowarm",
                                        "verbose",
                                        "debug",
                                        "help",
                                        ])
        except getopt.error, msg:
            raise Usage(msg)

        configuration = None
        options = {}

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
            elif o in ("-f", "--configure"):
                configuration = dict(x.split('=') for x in a.split(','))

        if (debug):
            logging.getLogger("storperf").setLevel(logging.DEBUG)

        if (erase):
            response = requests.delete(
                'http://127.0.0.1:5000/api/v1.0/configure')
            if (response.status_code != 200):
                raise Usage(response.reason)
            return 0

        if (configuration is not None):
            response = requests.post(
                'http://127.0.0.1:5000/api/v1.0/configure', json=configuration)
            if (response.status_code != 200):
                raise Usage(response.reason)

    except Usage, err:
        print >> sys.stderr, err.msg
        print >> sys.stderr, "for help use --help"
        return 2
    except UnknownWorkload, err:
        print >> sys.stderr, err.msg
        print >> sys.stderr, "for help use --help"
        return 2

    if (verbose):
        storperf._test_executor.register(event)

    if (report is not None):
        print storperf.fetch_results(report, workloads)
    else:
        while (storperf.is_stack_created == False):
            time.sleep(1)
        print "Ready to run"
        response = requests.post(
            'http://127.0.0.1:5000/api/v1.0/start', json=options)
        print response
        if (not response.ok):
            print html2text.html2text(response.content)
            raise Usage(response.reason)


if __name__ == "__main__":
    sys.exit(main())
