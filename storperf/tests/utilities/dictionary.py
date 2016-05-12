##############################################################################
# Copyright (c) 2015 EMC and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

import unittest
from utilities import dictionary


class DictionaryTest(unittest.TestCase):

    def setUp(self):
        self.dictionary = {}
        self.dictionary['key'] = 'value'
        pass

    def test_get_no_default(self):
        expected = None
        actual = dictionary.get_key_from_dict(self.dictionary, 'no-key')
        self.assertEqual(expected, actual)

    def test_get_with_default(self):
        expected = 'value 2'
        actual = dictionary.get_key_from_dict(
            self.dictionary, 'no-key', expected)
        self.assertEqual(expected, actual)

    def test_get_with_value(self):
        expected = 'value'
        actual = dictionary.get_key_from_dict(
            self.dictionary, 'key')
        self.assertEqual(expected, actual)

    def test_get_with_value_and_default(self):
        expected = 'value'
        actual = dictionary.get_key_from_dict(
            self.dictionary, 'key', 'value 2')
        self.assertEqual(expected, actual)
