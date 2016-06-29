##############################################################################
# Copyright (c) 2016 CENGN and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import unittest
from storperf.utilities.math import math

class MathTest(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)
        pass

    def test_slope_empty_series(self):
        expected = 0
        actual = math.slope([])
        self.assertEqual(expected, actual)

    def test_slope_integer_series(self):
        expected = 1.4
        actual = math.slope([[1,6], [2,5], [3,7], [4,10]])
        self.assertEqual(expected, actual)

    def test_slope_decimal_series(self):
        expected = 1.4
        actual = math.slope([[1.0,6.0], [2.0,5.0], [3.0,7.0], [4.0,10.0]])
        self.assertEqual(expected, actual)

    def test_slope_decimal_integer_mix(self):
        expected = 1.4
        actual = math.slope([[1.0,6], [2,5.0], [3,7], [4.0,10]])
        self.assertEqual(expected, actual)

    def test_slope_negative_y_series(self):
        expected = 2
        actual = math.slope([[1.0,-2], [2,2], [3,2]])
        self.assertEqual(expected, actual)

    def test_slope_negative_x_series(self):
        expected = 1.4
        actual = math.slope([[-24,6.0], [-23,5], [-22,7.0], [-21,10]])
        self.assertEqual(expected, actual)

    def test_slope_out_of_order_series(self):
        expected = 1.4
        actual = math.slope([[2,5.0], [4,10], [3.0,7], [1,6]])
        self.assertEqual(expected, actual)

    def test_slope_0_in_y(self):
        expected = -0.5
        actual = math.slope([[15.5,1], [16.5,0], [17.5,0]])
        self.assertEqual(expected, actual)

    def test_slope_0_in_x(self):
        expected = 1.4
        actual = math.slope([[0,6.0], [1,5], [2,7], [3,10]])
        self.assertEqual(expected, actual)

    def test_slope_0_in_x_and_y(self):
        expected = 1.5
        actual = math.slope([[0.0,0], [1,1], [2,3]])
        self.assertEqual(expected, actual)
