##############################################################################
# Copyright (c) 2016 CENGN and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
from random import uniform, randrange
import unittest

from storperf.utilities import math as Range


class MathRangeTest(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

    def test_empty_series(self):
        expected = None
        data_series = []
        actual = Range.range_value(data_series)
        self.assertEqual(expected, actual)

    def test_integer_series(self):
        expected = 11946
        data_series = [5, 351, 847, 2, 1985, 18,
                       96, 389, 687, 1, 11947, 758, 155]
        actual = Range.range_value(data_series)
        self.assertEqual(expected, actual)

    def test_float_series_1_decimal(self):
        expected = 778595.5
        data_series = [736.4, 9856.4, 684.2, 0.3, 0.9, 778595.8]
        actual = Range.range_value(data_series)
        self.assertEqual(expected, actual)

    def test_float_series_2_decimals(self):
        expected = 5693.47
        data_series = [51.36, 78.40, 1158.24, 5.50, 0.98, 5694.45]
        actual = Range.range_value(data_series)
        self.assertEqual(expected, actual)

    def test_float_series_3_decimals(self):
        expected = 992.181
        data_series = [4.562, 12.582, 689.452,
                       135.162, 996.743, 65.549, 36.785]
        actual = Range.range_value(data_series)
        self.assertEqual(expected, actual)

    def test_float_series_4_decimals(self):
        expected = 122985.3241
        data_series = [39.4785, 896.7845, 11956.3654,
                       44.2398, 6589.7134, 0.3671, 122985.6912]
        actual = Range.range_value(data_series)
        self.assertEqual(expected, actual)

    def test_float_series_5_decimals(self):
        expected = 8956208.84494
        data_series = [12.78496, 55.91275, 668.94378,
                       550396.5671, 512374.9999, 8956221.6299]
        actual = Range.range_value(data_series)
        self.assertEqual(expected, actual)

    def test_float_series_10_decimals(self):
        expected = 5984.507397972699
        data_series = [1.1253914785, 5985.6327894512,
                       256.1875693287, 995.8497623415]
        actual = Range.range_value(data_series)
        self.assertEqual(expected, actual)

    def test_float_mix(self):
        expected = 60781.6245372199
        data_series = [60785.9962, 899.4, 78.66, 69.58, 4.93795,
                       587.195486, 96.7694536, 5.13755964,
                       33.333333334, 60786.5624872199]
        actual = Range.range_value(data_series)
        self.assertEqual(expected, actual)

    def test_float_integer_mix(self):
        expected = 460781.05825
        data_series = [460785.9962, 845.634, 24.1, 69.58, 89, 4.93795]
        actual = Range.range_value(data_series)
        self.assertEqual(expected, actual)

    def test_negative_values(self):
        expected = 596.78163
        data_series = [-4.655, -33.3334, -596.78422, -0.00259, -66.785]
        actual = Range.range_value(data_series)
        self.assertEqual(expected, actual)

    def test_negative_positive_mix(self):
        expected = 58.859500000000004
        data_series = [6.85698, -2.8945, 0, -0.15, 55.965]
        actual = Range.range_value(data_series)
        self.assertEqual(expected, actual)

    def test_single_element(self):
        expected = 0
        data_series = [2.265]
        actual = Range.range_value(data_series)
        self.assertEqual(expected, actual)

    def test_10000_values_processing(self):
        expected = 28001.068
        data_series = [uniform(-10000, 10000) for _ in range(10000)]
        data_series.insert(randrange(len(data_series)), 15000.569)
        data_series.insert(randrange(len(data_series)), -13000.499)
        actual = Range.range_value(data_series)
        self.assertEqual(expected, actual)

    def test_processing_100_values_100_times(self):
        expected = 35911.3134
        for _ in range(1, 100):
            data_series = [uniform(-10000, 10000) for _ in range(100)]
            data_series.insert(randrange(len(data_series)), 16956.3334)
            data_series.insert(randrange(len(data_series)), -18954.98)
            actual = Range.range_value(data_series)
            self.assertEqual(expected, actual)

    def test_min_series(self):
        expected = [[1, 5.6], [2, 5.6], [3, 5.6], [4, 5.6]]
        data_series = [[1, 6], [2, 5], [3, 7], [4, 10]]
        actual = Range.min_series(data_series)
        self.assertEqual(expected, actual)

    def test_max_series(self):
        expected = [[1, 8.4], [2, 8.4], [3, 8.4], [4, 8.4]]
        data_series = [[1, 6], [2, 5], [3, 7], [4, 10]]
        actual = Range.max_series(data_series)
        self.assertEqual(expected, actual)
