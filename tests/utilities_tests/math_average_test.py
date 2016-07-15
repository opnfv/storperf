##############################################################################
# Copyright (c) 2016 CENGN and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import unittest
from storperf.utilities import math as math


class MathAverageTest(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

    def test_empty_series(self):
        expected = None
        data_series = []
        actual = math.average(data_series)
        self.assertEqual(expected, actual)

    def test_integer_series(self):
        expected = 19.75
        data_series = [5, 12, 7, 55]
        actual = math.average(data_series)
        self.assertEqual(expected, actual)

    def test_float_series(self):
        expected = 63.475899999999996
        data_series = [78.6, 45.187, 33.334, 96.7826]
        actual = math.average(data_series)
        self.assertEqual(expected, actual)

    def test_float_int_mix(self):
        expected = 472.104
        data_series = [10, 557.33, 862, 56.99, 874.2]
        actual = math.average(data_series)
        self.assertEqual(expected, actual)

    def test_negative_values(self):
        expected = -17.314
        data_series = [-15.654, 59.5, 16.25, -150, 3.334]
        actual = math.average(data_series)
        self.assertEqual(expected, actual)

    def test_single_value(self):
        expected = -66.6667
        data_series = [-66.6667]
        actual = math.average(data_series)
        self.assertEqual(expected, actual)
