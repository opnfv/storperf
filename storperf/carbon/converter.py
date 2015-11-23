##############################################################################
# Copyright (c) 2015 EMC and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import calendar
import logging
import time


class JSONToCarbon(object):

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def convert_to_dictionary(self, json_object, prefix=None):
        # Use the timestamp reported by fio, or current time if
        # not present.
        if 'timestamp' in json_object:
            timestamp = str(json_object.pop('timestamp'))
        else:
            timestamp = str(calendar.timegm(time.gmtime()))

        self.flat_dictionary = {}
        self.flat_dictionary['timestamp'] = timestamp

        self.resurse_to_flat_dictionary(json_object, prefix)
        return self.flat_dictionary

    def resurse_to_flat_dictionary(self, json, prefix=None):
        if type(json) == dict:
            for k, v in json.items():
                if prefix is None:
                    key = k.decode("utf-8").replace(" ", "_")
                else:
                    key = prefix + "." + k.decode("utf-8").replace(" ", "_")
                if hasattr(v, '__iter__'):
                    self.resurse_to_flat_dictionary(v, key)
                else:
                    self.flat_dictionary[key] = str(v).replace(" ", "_")
        elif type(json) == list:
            index = 0
            for v in json:
                index += 1
                if hasattr(v, '__iter__'):
                    self.resurse_to_flat_dictionary(
                        v, prefix + "." + str(index))
                else:
                    if prefix is None:
                        self.flat_dictionary[index] = str(v).replace(" ", "_")
                        + " " + self.timestamp
                    else:
                        key = prefix + "." + index
                        self.flat_dictionary[key] = str(v).replace(" ", "_")
