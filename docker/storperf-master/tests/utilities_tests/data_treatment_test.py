##############################################################################
# Copyright (c) 2016 CENGN and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import unittest
from storperf.utilities import data_treatment as DataTreatment


class DataTreatmentTest(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

    def test_empty_series(self):
        expected = {
            'slope_data': [],
            'range_data': [],
            'average_data': []
        }
        data_series = []
        actual = DataTreatment.data_treatment(data_series)
        self.assertEqual(expected, actual)

    def test_integer_series(self):
        expected = {
            'slope_data': [[1, 5], [66, 2], [12, 98], [74, 669], [33, 66]],
            'range_data': [5, 2, 98, 669, 66],
            'average_data': [5, 2, 98, 669, 66]
        }
        data_series = [[1, 5], [66, 2], [12, 98], [74, 669], [33, 66]]
        actual = DataTreatment.data_treatment(data_series)
        self.assertEqual(expected, actual)

    def test_float_series(self):
        expected = {
            'slope_data': [[5.6, 12.7], [96.66, 78.212],
                           [639.568, 5.3], [4.65, 6.667]],
            'range_data': [12.7, 78.212, 5.3, 6.667],
            'average_data': [12.7, 78.212, 5.3, 6.667]
        }
        data_series = [
            [5.6, 12.7], [96.66, 78.212], [639.568, 5.3], [4.65, 6.667]]
        actual = DataTreatment.data_treatment(data_series)
        self.assertEqual(expected, actual)

    def test_float_int_mix(self):
        expected = {
            'slope_data': [[5, 12.7], [96.66, 7], [639.568, 5.3], [4, 6]],
            'range_data': [12.7, 7, 5.3, 6],
            'average_data': [12.7, 7, 5.3, 6]
        }
        data_series = [[5, 12.7], [96.66, 7], [639.568, 5.3], [4, 6]]
        actual = DataTreatment.data_treatment(data_series)
        self.assertEqual(expected, actual)

    def test_negative_values(self):
        expected = {
            'slope_data': [[-15, 5.56], [41.3, -278], [41.3, -98],
                           [78.336, -0.12], [33.667, 66]],
            'range_data': [5.56, -278, -98, -0.12, 66],
            'average_data': [5.56, -278, -98, -0.12, 66]
        }
        data_series = [
            [-15, 5.56], [41.3, -278], [41.3, -98],
            [78.336, -0.12], [33.667, 66]]
        actual = DataTreatment.data_treatment(data_series)
        self.assertEqual(expected, actual)

    def test_single_value(self):
        expected = {
            'slope_data': [[86.8, 65.36]],
            'range_data': [65.36],
            'average_data': [65.36]
        }
        data_series = [[86.8, 65.36]]
        actual = DataTreatment.data_treatment(data_series)
        self.assertEqual(expected, actual)
