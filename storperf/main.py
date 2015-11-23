##############################################################################
# Copyright (c) 2015 EMC and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import getopt
import json
import logging.config
import os
import sys

from test_executor import TestExecutor, UnknownWorkload

"""
"""


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
    test_executor = TestExecutor()
    verbose = False
    workloads = None

    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "t:w:scvh",
                                       ["target=",
                                        "workload=",
                                        "nossd",
                                        "nowarm",
                                        "verbose",
                                        "help",
                                        ])
        except getopt.error, msg:
            raise Usage(msg)

        for o, a in opts:
            if o in ("-h", "--help"):
                print __doc__
                return 0
            elif o in ("-t", "--target"):
                test_executor.filename = a
            elif o in ("-v", "--verbose"):
                verbose = True
            elif o in ("-s", "--nossd"):
                test_executor.precondition = False
            elif o in ("-c", "--nowarm"):
                test_executor.warm = False
            elif o in ("-w", "--workload"):
                workloads = a.split(",")

        test_executor.register_workloads(workloads)

    except Usage, err:
        print >> sys.stderr, err.msg
        print >> sys.stderr, "for help use --help"
        return 2
    except UnknownWorkload, err:
        print >> sys.stderr, err.msg
        print >> sys.stderr, "for help use --help"
        return 2

    if (verbose):
        test_executor.register(event)

    test_executor.execute()

if __name__ == "__main__":
    sys.exit(main())
