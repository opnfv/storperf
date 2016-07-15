##############################################################################
# Copyright (c) 2016 CENGN and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
from storperf.utilities import data_treatment as DataTreatment
from storperf.utilities import math as math


def steady_state(data_series):
    """
    This function seeks to detect steady state given on a measurement
    window given the data series of that measurement window following
    the pattern : [[x1,y1], [x2,y2], ..., [xm,ym]]. m represents the number
    of points recorded in the measurement window, x which represents the
    time, and y which represents the Volume performance variable being
    tested e.g. IOPS, latency...
    The function returns a boolean describing wether or not steady state
    has been reached with the data that is passed to it.
    """

    # Pre conditioning the data to match the algorithms
    treated_data = DataTreatment.data_treatment(data_series)

    # Calculating useful values invoking dedicated functions
    slope_value = math.slope(treated_data['slope_data'])
    range_value = math.range_value(treated_data['range_data'])
    average_value = math.average(treated_data['average_data'])

    if (slope_value is not None and range_value is not None and
            average_value is not None):
        # Verification of the Steady State conditions following the SNIA
        # definition
        range_condition = range_value < 0.20 * abs(average_value)
        slope_condition = slope_value < 0.10 * abs(average_value)

        steady_state = range_condition and slope_condition

    else:
        steady_state = False

    return steady_state
