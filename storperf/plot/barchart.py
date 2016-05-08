##############################################################################
# Copyright (c) 2015 EMC and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

import cStringIO

import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as pyplot
import numpy as np


class Barchart(object):

    def __init__(self):
        pass

    def barchart(self, queue_depths, block_sizes, read_latencies):
        pyplot.figure()

        y_pos = np.arange(len(block_sizes))
        bar_width = 0.15

        colors = ['r', 'g', 'b', 'y']
        legend = []
        index = 0
        for series in queue_depths:
            chart = pyplot.bar(y_pos + (bar_width * index),
                               read_latencies[index],
                               bar_width,
                               color=colors[index],
                               align='center',
                               label="Queue Depth " + str(series),
                               alpha=0.4)
            legend.append(chart[0])
            index += 1

        pyplot.xticks(y_pos + bar_width, block_sizes)
        pyplot.ylabel("Latency (Microseconds)")
        pyplot.xlabel("Block Sizes (bytes)")
        pyplot.title("Latency Report")
        pyplot.legend()
        pyplot.tight_layout()

    def to_base64_image(self):
        sio = cStringIO.StringIO()
        pyplot.savefig(sio, format="png")
        return sio.getvalue().encode("base64").strip()
