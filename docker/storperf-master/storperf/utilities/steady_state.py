##############################################################################
# Copyright (c) 2016 CENGN and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import logging

from storperf.utilities import data_treatment as DataTreatment
from storperf.utilities import math
from storperf.utilities.math import RANGE_DEVIATION, SLOPE_DEVIATION


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

    logger = logging.getLogger('storperf.utilities.steady_state')

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
        range_condition = abs(range_value) <= RANGE_DEVIATION * \
            abs(average_value)
        slope_condition = abs(slope_value) <= SLOPE_DEVIATION * \
            abs(average_value)

        steady_state = range_condition and slope_condition

        logger.debug("Range %s <= %s?" % (abs(range_value),
                                          (RANGE_DEVIATION *
                                           abs(average_value))))
        logger.debug("Slope %s <= %s?" % (abs(slope_value),
                                          (SLOPE_DEVIATION *
                                           abs(average_value))))
        logger.debug("Steady State? %s" % steady_state)
    else:
        steady_state = False

    return steady_state
