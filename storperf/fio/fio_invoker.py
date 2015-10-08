##############################################################################
# Copyright (c) 2015 EMC and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

import sys
import getopt
import subprocess
import json
from threading  import Thread

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg
        
class FIOInvoker(object):
    def __init__(self):
        self.event_listeners = set()
        
    def register(self, event_listener):
        self.event_listeners.add(event_listener)

    def unregister(self, event_listener):
        self.event_listeners.discard(event_listener)
        
    def stdout_handler(self):
        self.json_body = ""
        for line in iter(self.fio_process.stdout.readline, b''):
            self.json_body += line
            try:
                json_metric = json.loads(self.json_body)
                self.json_body = ""
                
                for event_listener in self.event_listeners:
                    event_listener(json_metric)

            except:
                if self.json_body.startswith("fio"):
                    self.json_body = ""
                pass

        self.fio_process.stdout.close()

    def stderr_handler(self):
        for line in iter(self.fio_process.stderr.readline, b''):
            print line

        self.fio_process.stderr.close()
        
    def execute(self, args=[]):          
        self.fio_process = subprocess.Popen(['fio']+args,
                                            universal_newlines=True, stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE);
        
        t = Thread(target=self.stdout_handler, args=())
        t.daemon = False
        t.start()
        
        t = Thread(target=self.stderr_handler, args=())
        t.daemon = False
        t.start()

        # fio --rw=randread --size=32m --directory=/tmp/fio-testing/data --ioengine=libaio --iodepth=2 --direct=1 --invalidate=1 --numjobs=4 --name=random-read
        
def event(json_metric):
    print json_metric
        

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
                    '--time_based', '--runtime=6']

    invoker = FIOInvoker()
    invoker.register(event)
    invoker.execute(simple_args)

if __name__ == "__main__":
    sys.exit(main())
