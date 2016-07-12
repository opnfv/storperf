##############################################################################
# Copyright (c) 2016 CENGN and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

class MathRange(object):

    @staticmethod
    def range(data_series):
        """
        This function implements a range algorithm that returns a float number
        representing the range of the data_series that is passed to it.
        The data_series being passed is assumed to follow the following data
        pattern : [y1, y2, y3, ..., yn] where yi represents the ith
        measuring point of the y variable. The y variable represents the
        Volume performance being tested (e.g. IOPS, latency...).
        The conversion of the data series from the original pattern to the
        [y1, y2, y3, ..., yn] pattern is done outside this function
        so the original pattern can be changed without breaking this function.
        """

        if len(data_series) == 0: #In the particular case of an empty data series
            range_value = 0

        else: #The general case
            max_value = max(data_series)
            min_value = min(data_series)
            range_value = max_value - min_value

        return range_value
