##############################################################################
# Copyright (c) 2015 EMC and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import getopt
import socket
import sys

from fio.fio_invoker import FIOInvoker
from carbon.emitter import CarbonMetricTransmitter
from carbon.converter import JSONToCarbon

"""
"""

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

def event(metric):
    metrics_converter = JSONToCarbon()
    metrics_emitter = CarbonMetricTransmitter()
    prefix = socket.getfqdn()
    carbon_metrics = metrics_converter.convert_to_dictionary(metric, prefix)
    metrics_emitter.transmit_metrics(carbon_metrics)

def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        try:
            opts = getopt.getopt(argv[1:], "h", ["help"])
        except getopt.error, msg:
            raise Usage(msg)
        
    except Usage, err:
        print >> sys.stderr, err.msg
        print >> sys.stderr, "for help use --help"
        return 2
    
    for o in opts:
        if o in ("-h", "--help"):
            print __doc__
            return 0
        
    simple_args = ['--rw=randread', '--size=32m', 
                    '--directory=.',
                    '--iodepth=2', 
                    '--direct=1', '--invalidate=1', '--numjobs=4',
                    '--name=random-read', '--output-format=json',
                    '--status-interval=3', 
                    '--time_based', '--runtime=60']

    invoker = FIOInvoker()
    invoker.register(event)
    invoker.execute(simple_args)

if __name__ == "__main__":
    sys.exit(main())
