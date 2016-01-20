##############################################################################
# Copyright (c) 2015 EMC and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

from _sqlite3 import OperationalError
import logging
import sqlite3


class ConfigurationDB(object):

    db_name = "StorPerf.db"

    def __init__(self):
        """
        Creates the StorPerf.db and configuration tables on demand
        """

        self.logger = logging.getLogger(__name__)
        self.logger.debug("Connecting to " + ConfigurationDB.db_name)
        db = sqlite3.connect(ConfigurationDB.db_name)

        cursor = db.cursor()
        try:
            cursor.execute('''CREATE TABLE configuration
            (configuration_name text,
            key text,
            value text)''')
            self.logger.debug("Created configuration table")
        except OperationalError:
            self.logger.debug("Configuration table exists")

        cursor.execute('SELECT * FROM configuration')

    def delete_configuration_value(self, configuration_name, key):
        """Deletes the value associated with the given key
        """

        db = sqlite3.connect(ConfigurationDB.db_name)
        cursor = db.cursor()

        cursor.execute(
            "delete from configuration where configuration_name=? and key=?",
            (configuration_name, key))

        self.logger.debug("Deleted " + configuration_name + ":" + key)

        db.commit()

    def get_configuration_value(self, configuration_name, key):
        """Returns a string representation of the value stored
        with this key under the given configuration name.
        """

        db = sqlite3.connect(ConfigurationDB.db_name)
        cursor = db.cursor()

        cursor.execute(
            """select value from configuration
                       where configuration_name = ?
                       and key = ?""",
            (configuration_name, key,))

        row = cursor.fetchone()

        if (row is None):
            self.logger.debug(
                configuration_name + ":" + key + " does not exist")
            return None
        else:
            self.logger.debug(
                configuration_name + ":" + key + " is " + str(row[0]))
            return str(row[0])

    def set_configuration_value(self, configuration_name, key, value):
        """Updates or creates the key under the given configuration
        name so that it holds the value specified.
        """

        if (value is None):
            return self.delete_configuration_value(configuration_name, key)

        value = str(value)

        db = sqlite3.connect(ConfigurationDB.db_name)
        cursor = db.cursor()

        cursor.execute(
            "delete from configuration where configuration_name=? and key=?",
            (configuration_name, key))

        cursor.execute(
            """insert into configuration(configuration_name, key, value)
             values (?,?,?)""", (configuration_name, key, value))

        self.logger.debug(configuration_name + ":" + key + " set to " + value)

        db.commit()
