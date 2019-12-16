##############################################################################
# Copyright (c) 2017 Dell EMC and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

import json
import unittest

from storperf.fio.fio_invoker import FIOInvoker
from io import BytesIO


class Test(unittest.TestCase):

    simple_dictionary = {'Key': 'Value'}

    def exceptional_event(self, callback_id, metric):
        self.exception_called = True
        raise Exception

    def event(self, callback_id, metric):
        self.metric = metric

    def setUp(self):
        self.exception_called = False
        self.metric = None
        self.fio_invoker = FIOInvoker()

    def testStdoutValidJSON(self):
        self.fio_invoker.register(self.event)
        string = json.dumps(self.simple_dictionary, indent=4, sort_keys=True)

        output = BytesIO((string + "\n").encode('utf-8'))
        self.fio_invoker.stdout_handler(output)

        self.assertEqual(self.simple_dictionary, self.metric)

    def testStdoutValidJSONWithFIOOutput(self):
        self.fio_invoker.register(self.event)
        string = json.dumps(self.simple_dictionary, indent=4, sort_keys=True)
        terminating = "fio: terminating on signal 2\n"
        output = BytesIO((terminating + string + "\n").encode('utf-8'))
        self.fio_invoker.stdout_handler(output)

        self.assertEqual(self.simple_dictionary, self.metric)

    def testStdoutNoJSON(self):
        self.fio_invoker.register(self.event)
        string = "{'key': 'value'}"

        output = BytesIO((string + "\n").encode('utf-8'))
        self.fio_invoker.stdout_handler(output)

        self.assertEqual(None, self.metric)

    def testStdoutInvalidJSON(self):
        self.fio_invoker.register(self.event)
        string = "{'key':\n}"

        output = BytesIO((string + "\n").encode('utf-8'))
        self.fio_invoker.stdout_handler(output)

        self.assertEqual(None, self.metric)

    def testStdoutAfterTerminated(self):
        self.fio_invoker.register(self.event)
        string = json.dumps(self.simple_dictionary, indent=4, sort_keys=True)

        self.fio_invoker.terminated = True
        output = BytesIO((string + "\n").encode('utf-8'))
        self.fio_invoker.stdout_handler(output)

        self.assertEqual(None, self.metric)

    def testStdoutCallbackException(self):
        self.fio_invoker.register(self.exceptional_event)
        self.fio_invoker.register(self.event)
        string = json.dumps(self.simple_dictionary, indent=4, sort_keys=True)

        output = BytesIO((string + "\n").encode('utf-8'))
        self.fio_invoker.stdout_handler(output)

        self.assertEqual(self.simple_dictionary, self.metric)
        self.assertEqual(self.exception_called, True)
