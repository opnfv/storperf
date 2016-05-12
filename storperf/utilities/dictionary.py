##############################################################################
# Copyright (c) 2015 EMC and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################


def get_key_from_dict(dictionary, key, default_value=None):
    if key in dictionary:
        return dictionary[key]
    else:
        return default_value
