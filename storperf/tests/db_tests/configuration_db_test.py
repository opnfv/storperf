##############################################################################
# Copyright (c) 2015 EMC and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

import unittest

from db.configuration_db import ConfigurationDB


class ConfigurationDBTest(unittest.TestCase):

    def setUp(self):
        ConfigurationDB.db_name = ":memory:"
        self.config_db = ConfigurationDB()

    def test_create_key(self):
        expected = "ABCDE-12345"

        self.config_db.set_configuration_value(
            "test", "key", expected)

        actual = self.config_db.get_configuration_value(
            "test", "key")

        self.assertEqual(
            expected, actual, "Did not expect: " + str(actual))

    def test_update_key(self):
        expected = "ABCDE-12345"

        self.config_db.set_configuration_value(
            "test", "key", "initial_value")

        self.config_db.set_configuration_value(
            "test", "key", expected)

        actual = self.config_db.get_configuration_value(
            "test", "key")

        self.assertEqual(
            expected, actual, "Did not expect: " + str(actual))

    def test_deleted_key(self):
        expected = None

        self.config_db.set_configuration_value(
            "test", "key", "initial_value")

        self.config_db.delete_configuration_value(
            "test", "key")

        actual = self.config_db.get_configuration_value(
            "test", "key")

        self.assertEqual(
            expected, actual, "Did not expect: " + str(actual))
