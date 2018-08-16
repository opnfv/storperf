##############################################################################
# Copyright (c) 2016 CENGN and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import copy

RANGE_DEVIATION = 0.20
SLOPE_DEVIATION = 0.10


def slope(data_series):
    """
    This function implements the linear least squares algorithm described in
    the following wikipedia article :
    https://en.wikipedia.org/wiki/Linear_least_squares_(mathematics)
    in the case of m equations (provided by m data points) and 2 unknown
    variables (x and y, which represent the time and the Volume performance
    variable being tested e.g. IOPS, latency...).
    The data_series is currently assumed to follow the pattern :
    [[x1,y1], [x2,y2], ..., [xm,ym]].
    If this data pattern were to change, the data_treatement function
    should be adjusted to ensure compatibility with the rest of the
    Steady State Detection module.
    """

    # In the particular case of an empty data series
    if len(data_series) == 0:
        beta2 = None

    else:  # The general case
        data_series = copy.deepcopy(data_series)
        m = len(data_series)
        # To make sure at least one element is a float number so the result
        # of the algorithm be a float number
        data_series[0][0] = float(data_series[0][0])

        """
        It consists in solving the normal equations system (2 equations,
        2 unknowns) by calculating the value of beta2 (slope).
        The formula of beta1 (the y-intercept) is given as a comment in
        case it is needed later.
        """
        sum_xi = 0
        sum_xi_sq = 0
        sum_yi_xi = 0
        sum_yi = 0
        for i in range(0, m):
            xi = data_series[i][0]
            yi = data_series[i][1]

            sum_xi += xi
            sum_xi_sq += xi**2
            sum_yi_xi += xi * yi
            sum_yi += yi

        over = (sum_xi**2 - m * sum_xi_sq)
        if over == 0:
            beta2 = None  # Infinite slope
        else:
            beta2 = (sum_yi * sum_xi - m * sum_yi_xi) / over  # The slope
        # beta1 = (sum_yi_xi - beta2*sum_xi_sq)/sum_xi #The y-intercept if
        # needed

    return beta2


def range_value(data_series):
    """
    This function implements a range algorithm that returns a float number
    representing the range of the data_series that is passed to it.
    The data_series being passed is assumed to follow the following data
    pattern : [y1, y2, y3, ..., ym] where yi represents the ith
    measuring point of the y variable. The y variable represents the
    Volume performance being tested (e.g. IOPS, latency...).
    If this data pattern were to change, the data_treatment function
    should be adjusted to ensure compatibility with the rest of the
    Steady State Dectection module.
    The conversion of the data series from the original pattern to the
    [y1, y2, y3, ..., ym] pattern is done outside this function
    so the original pattern can be changed without breaking this function.
    """

    # In the particular case of an empty data series
    if len(data_series) == 0:
        range_value = None

    else:  # The general case
        max_value = max(data_series)
        min_value = min(data_series)
        range_value = max_value - min_value

    return range_value


def average(data_series):
    """
    This function seeks to calculate the average value of the data series
    given a series following the pattern : [y1, y2, y3, ..., ym].
    If this data pattern were to change, the data_treatment function
    should be adjusted to ensure compatibility with the rest of the
    Steady State Dectection module.
    The function returns a float number corresponding to the average of the yi.
    """
    m = len(data_series)

    if m == 0:  # In the particular case of an empty data series
        average = None

    else:
        data_sum = 0
        for value in data_series:
            data_sum += value
        average = data_sum / float(m)

    return average


def slope_series(data_series):
    """
    This function returns an adjusted series based on the average
    for the supplied series and the slope of the series.
    """

    new_series = []
    average_series = []
    for l in data_series:
        average_series.append(l[1])

    avg = average(average_series)
    slp = slope(data_series)

    if slp is None or avg is None:
        return new_series

    multiplier = float(len(data_series) + 1) / 2.0 - len(data_series)
    for index, _ in data_series:
        new_value = avg + (slp * multiplier)
        new_series.append([index, new_value])
        multiplier += 1

    return new_series


def min_series(data_series):
    """
    This function returns an copy of the series with only the
    minimum allowed deviation as its values
    """

    new_series = []
    average_series = []
    for l in data_series:
        average_series.append(l[1])
    avg = average(average_series)
    low = avg - (avg * RANGE_DEVIATION)

    for index, _ in data_series:
        new_series.append([index, low])

    return new_series


def max_series(data_series):
    """
    This function returns an copy of the series with only the
    maximum allowed deviation as its values
    """

    new_series = []
    average_series = []
    for l in data_series:
        average_series.append(l[1])
    avg = average(average_series)
    high = avg + (avg * RANGE_DEVIATION)

    for index, _ in data_series:
        new_series.append([index, high])

    return new_series
