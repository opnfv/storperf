##############################################################################
# Copyright (c) 2016 CENGN and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################


def data_treatment(data_series):
    """
    This function aims at performing any necessary pre treatment on the
    data_series passed to the steady_state function before being passed
    under to the different math utilities (slope, range and average)
    so the data can match the requirements of each algorithm.
    The function returns a dictionary composed of three values that can be
    accessed with the following keys : 'slope_data', 'range_data' and
    'average_data'.
    The data_series is currently assumed to follow the pattern :
    [[x1,y1], [x2,y2], ..., [xm,ym]]. If this pattern were to change, or
    the input data pattern of one of the math module, this data_treatment
    function should be the only part of the Steady State detection module
    that would need to be modified too.
    """

    x_values = []
    y_values = []
    for l in data_series:
        x_values.append(l[0])
        y_values.append(l[1])

    treated_data = {
        'slope_data': data_series,  # No treatment necessary so far
        'range_data': y_values,  # The y_values only
        'average_data': y_values
    }

    return treated_data
