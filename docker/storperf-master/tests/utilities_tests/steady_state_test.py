##############################################################################
# Copyright (c) 2016 CENGN and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import unittest
from storperf.utilities import steady_state as SteadyState


class SteadyStateTest(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

    def test_integer_values(self):
        expected = True
        data_series = [[305, 20], [306, 21], [307, 21], [308, 19]]
        actual = SteadyState.steady_state(data_series)
        self.assertEqual(expected, actual)

    def test_float_values(self):
        expected = True
        data_series = [
            [55.5, 40.5], [150.2, 42.3], [150.8, 41.8], [151.2, 41.5]]
        actual = SteadyState.steady_state(data_series)
        self.assertEqual(expected, actual)

    def test_float_integer_mix_false(self):
        expected = False
        data_series = [[1, 2], [2, 2.2], [3, 1.8], [4, 1.8]]
        actual = SteadyState.steady_state(data_series)
        self.assertEqual(expected, actual)

    def test_float_integer_mix_true(self):
        expected = True
        data_series = [[12, 18], [12.5, 18.2], [13, 16.8], [15, 16.8]]
        actual = SteadyState.steady_state(data_series)
        self.assertEqual(expected, actual)

    def test_empty_series(self):
        expected = False
        data_series = []
        actual = SteadyState.steady_state(data_series)
        self.assertEqual(expected, actual)

    def test_negative_values(self):
        expected = True
        data_series = [[-1, -24.2], [0.5, -23.8], [1.1, -24.0], [3.2, -24.0]]
        actual = SteadyState.steady_state(data_series)
        self.assertEqual(expected, actual)

    def test_out_of_order_series(self):
        expected = True
        data_series = [[-15, 0.43], [-16, 0.41], [-3, 0.45], [4, 0.42]]
        actual = SteadyState.steady_state(data_series)
        self.assertEqual(expected, actual)

    def test_negative_slope(self):
        expected = False
        data_series = [[1.3, 1], [1.2, 1], [1.1, 1.1], [1.0, 1.1]]
        actual = SteadyState.steady_state(data_series)
        self.assertEqual(expected, actual)
