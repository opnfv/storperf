##############################################################################
# Copyright (c) 2016 CENGN and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

class math(object):
    
    @staticmethod
    def slope(data_series):
        """
        This function implements the linear least squares algorithm described in the following wikipedia article
        https://en.wikipedia.org/wiki/Linear_least_squares_(mathematics) 
        in the case of m equations (provided by m data points) and 2 unknown variables (x and 
        y, which represent the time and the Volume performance variable being 
        tested e.g. IOPS, latency...)
        """
        
        if len(data_series)==0: #In the particular case of an empty data series 
            beta2 = 0
            
        else: #The general case
            m = len(data_series) #given a [[x1,y1], [x2,y2], ..., [xm,ym]] data series
            data_series[0][0] = float(data_series[0][0]) #To make sure at least one element is a float number so the result of the algorithm be a float number
            
            """
            It consists in solving the normal equations system (2 equations, 2 unknowns)
            by calculating the value of beta2 (slope). The formula of beta1 (the y-intercept)
            is given as a comment in case it is needed later.
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
                sum_yi_xi += xi*yi
                sum_yi += yi
            
            beta2 = (sum_yi*sum_xi - m*sum_yi_xi)/(sum_xi**2 - m*sum_xi_sq) #The slope
            #beta1 = (sum_yi_xi - beta2*sum_xi_sq)/sum_xi #The y-intercept if needed
        
        return beta2
            
        
        