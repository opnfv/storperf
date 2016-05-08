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
from mpl_toolkits.mplot3d import Axes3D
import numpy as np


class Barchart(object):

    def __init__(self):
        pass

    def barchart3d(self, queue_depths, block_sizes, latencies, c, title):

        fig = pyplot.figure()

        #ax = Axes3D(fig)

        data = np.array(latencies)

        lx = len(data[0])          # Work out matrix dimensions
        ly = len(data[:, 0])
        xpos = np.arange(0, lx, 1)    # Set up a mesh of positions
        ypos = np.arange(0, ly, 1)
        xpos, ypos = np.meshgrid(xpos + 0.25, ypos + 0.25)

        xpos = xpos.flatten()   # Convert positions to 1D array
        ypos = ypos.flatten()
        zpos = np.zeros(lx * ly)

        dx = 0.5 * np.ones_like(zpos)
        dy = dx.copy()
        dz = data.flatten()

        ax = fig.add_subplot(111, projection='3d')
        ax.bar3d(xpos, ypos, zpos, dx, dy, dz, color=c)

        ticksx = np.arange(0.5, len(block_sizes), 1)
        pyplot.xticks(ticksx, block_sizes)

        ticksy = np.arange(0.6, len(queue_depths), 1)
        pyplot.yticks(ticksy, queue_depths)

        ax.set_xlabel('Block Size')
        ax.set_ylabel('Queue Depth')
        ax.set_zlabel(title)

        ticksx = np.arange(0.5, 3, 1)
        pyplot.xticks(ticksx, block_sizes)

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
