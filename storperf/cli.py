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

import getopt
import json
import logging.config
import os
import sys
import time

from storperf_master import StorPerfMaster
from test_executor import UnknownWorkload


class Usage(Exception):

    def __init__(self, msg):
        self.msg = msg


def setup_logging(
    default_path='rest_server/logging.json',
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

        for o, a in opts:
            if o in ("-h", "--help"):
                print __doc__
                return 0
            elif o in ("-t", "--target"):
                storperf.filename = a
            elif o in ("-t", "--target"):
                report = a
            elif o in ("-v", "--verbose"):
                verbose = True
            elif o in ("-d", "--debug"):
                debug = True
            elif o in ("-s", "--nossd"):
                storperf.precondition = False
            elif o in ("-c", "--nowarm"):
                storperf.warm_up = False
            elif o in ("-w", "--workload"):
                workloads = a
            elif o in ("-r", "--report"):
                report = a
            elif o in ("-e", "--erase"):
                erase = True
            elif o in ("-f", "--configure"):
                configuration = dict(x.split('=') for x in a.split(','))

        if (debug):
            logging.getLogger().setLevel(logging.DEBUG)

        if (configuration is not None):
            if ('volume_size' in configuration):
                storperf.volume_size = configuration['volume_size']
            if ('agent_count' in configuration):
                storperf.agent_count = configuration['agent_count']
            if ('agent_network' in configuration):
                storperf.agent_network = configuration['agent_network']

            storperf.validate_stack()
            storperf.create_stack()

        if (erase):
            storperf.delete_stack()
            return 0

        storperf.workloads = workloads

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
        storperf.execute_workloads()

if __name__ == "__main__":
    sys.exit(main())
