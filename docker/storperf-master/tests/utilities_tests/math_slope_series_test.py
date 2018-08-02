##############################################################################
# Copyright (c) 2016 CENGN and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import unittest
from storperf.utilities import math


class MathSlopeSeriesTest(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)
        pass

    def test_slope_empty_series(self):
        expected = []
        actual = math.slope_series([])
        self.assertEqual(expected, actual)

    def test_slope_integer_series(self):
        expected = [[1, 4.9], [2, 6.3], [3, 7.7], [4, 9.1]]
        actual = math.slope_series([[1, 6], [2, 5], [3, 7], [4, 10]])
        self.assertEqual(expected, actual)

    def test_slope_mix_series(self):
        expected = [[1, 4.9], [2, 6.3], [3, 7.7], [4, 9.1]]
        actual = math.slope_series([[1.0, 6], [2, 5.0], [3, 7], [4.0, 10]])
        self.assertEqual(expected, actual)

    def test_slope_0_in_y(self):
        expected = [
            [15.5, 0.8333333333333333],
            [16.5, 0.3333333333333333],
            [17.5, -0.16666666666666669]]
        actual = math.slope_series([[15.5, 1], [16.5, 0], [17.5, 0]])
        self.assertEqual(expected, actual)

    def test_slope_gaps_in_x(self):
        expected = [
            [1, 1.3571428571428572],
            [2, 2.0],
            [4, 2.642857142857143]]
        actual = math.slope_series([[1, 1], [2, 2], [4, 3]])
        self.assertEqual(expected, actual)
