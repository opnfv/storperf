##############################################################################
# Copyright (c) 2015 EMC and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

from storperf.carbon.converter import JSONToCarbon
import json
import unittest


class JSONToCarbonTest(unittest.TestCase):

    single_json_text_element = """{ "key" : "value" }"""
    single_json_numeric_element = """{ "key" : 123 }"""
    single_json_key_with_spaces = """{ "key with spaces" : "value" }"""
    single_json_value_with_spaces = """{ "key" : "value with spaces" }"""
    json_map_name_with_spaces = \
        """{ "map with spaces" : { "key" : "value" } }"""
    json_list_name_with_spaces = \
        """{ "list with spaces" : [{ "key" : "value" }] }"""

    simple_fio_json = """
{
  "fio version" : "fio-2.2.10",
  "timestamp" : 1444144664,
  "time" : "Tue Oct  6 11:17:44 2015",
  "jobs" : [
    {
      "jobname" : "random-read",
      "groupid" : 0,
      "error" : 0,
      "eta" : 0,
      "elapsed" : 26,
      "read" : {
        "io_bytes" : 7116,
        "bw" : 275,
        "iops" : 68.99,
        "runtime" : 25788,
        "total_ios" : 1779,
        "short_ios" : 0,
        "drop_ios" : 0,
        "slat" : {
          "min" : 0,
          "max" : 0,
          "mean" : 0.00,
          "stddev" : 0.00
        }
      }
    }]
}
"""

    def setUp(self):
        pass

    def test_to_string(self):
        testconv = JSONToCarbon()
        json_object = json.loads(self.simple_fio_json)
        result = testconv.convert_to_dictionary(json_object, "host.run-name")
        self.assertEqual("7116", result[
                         "host.run-name.jobs.1.read.io_bytes"],
                         result["host.run-name.jobs.1.read.io_bytes"])

    def test_single_text_element_no_prefix(self):
        testconv = JSONToCarbon()
        result = testconv.convert_to_dictionary(
            json.loads(self.single_json_text_element))

        self.assertEqual("value", result["key"], result["key"])

    def test_single_numeric_element_no_prefix(self):
        testconv = JSONToCarbon()
        result = testconv.convert_to_dictionary(
            json.loads(self.single_json_numeric_element))

        self.assertEqual("123", result["key"], result["key"])

    def test_single_text_key_space_element_no_prefix(self):
        testconv = JSONToCarbon()
        result = testconv.convert_to_dictionary(
            json.loads(self.single_json_key_with_spaces))

        self.assertEqual(
            "value", result["key_with_spaces"], result["key_with_spaces"])

    def test_single_text_value_space_element_no_prefix(self):
        testconv = JSONToCarbon()
        result = testconv.convert_to_dictionary(
            json.loads(self.single_json_value_with_spaces))

        self.assertEqual("value_with_spaces", result["key"], result["key"])

    def test_map_name_with_space_no_prefix(self):
        testconv = JSONToCarbon()
        result = testconv.convert_to_dictionary(
            json.loads(self.json_map_name_with_spaces))

        self.assertEqual(
            "value", result["map_with_spaces.key"],
            result["map_with_spaces.key"])

    def test_list_name_with_space_no_prefix(self):
        testconv = JSONToCarbon()
        result = testconv.convert_to_dictionary(
            json.loads(self.json_list_name_with_spaces))

        self.assertEqual(
            "value", result["list_with_spaces.1.key"],
            result["list_with_spaces.1.key"])


if __name__ == '__main__':
    unittest.main()
