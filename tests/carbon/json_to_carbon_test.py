##############################################################################
# Copyright (c) 2015 EMC and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

import unittest

import json

import carbon.converter

class JSONToCarbonTest(unittest.TestCase):

    single_json_text_element = """{ "timestamp" : "timestamp", "key" : "value" }"""
    single_json_numeric_element = """{ "timestamp" : "timestamp", "key" : 123 }"""
    single_json_key_with_spaces = """{ "timestamp" : "timestamp", "key with spaces" : "value" }"""
    single_json_value_with_spaces = """{ "timestamp" : "timestamp", "key" : "value with spaces" }"""
    json_map_name_with_spaces = """{ "timestamp" : "timestamp", "map with spaces" : { "key" : "value" } }"""
    json_list_name_with_spaces = """{ "timestamp" : "timestamp", "list with spaces" : [{ "key" : "value" }] }"""

    sample_json = """
{
    "colorsArray":[{
            "colorName":"red",
            "hexValue":"#f00"
        },
        {
            "colorName":"green",
            "hexValue":"#0f0"
        },
        {
            "colorName":"blue",
            "hexValue":"#00f"
        }
    ]
}"""

    simple_fio_json = """
{
  "fio version" : "fio-2.2.10",
  "timestamp" : 1444144664,
  "time" : "Tue Oct  6 11:17:44 2015",
  "jobs" : [
    {
      "jobname" : "random-read",
      "groupid" : 0,
      "error" : 0,
      "eta" : 0,
      "elapsed" : 26,
      "read" : {
        "io_bytes" : 7116,
        "bw" : 275,
        "iops" : 68.99,
        "runtime" : 25788,
        "total_ios" : 1779,
        "short_ios" : 0,
        "drop_ios" : 0,
        "slat" : {
          "min" : 0,
          "max" : 0,
          "mean" : 0.00,
          "stddev" : 0.00
        }
      }
    }]
}
"""

    full_fio = """
{
  "fio version" : "fio-2.1.11",
  "jobs" : [
    {
      "jobname" : "random-read",
      "groupid" : 0,
      "error" : 0,
      "read" : {
        "io_bytes" : 44920,
        "bw" : 21,
        "iops" : 5,
        "runtime" : 2127550,
        "slat" : {
          "min" : 0,
          "max" : 0,
          "mean" : 0.00,
          "stddev" : 0.00
        },
        "clat" : {
          "min" : 53,
          "max" : 6329,
          "mean" : 255.34,
          "stddev" : 94.40,
          "percentile" : {
            "1.000000" : 84,
            "5.000000" : 181,
            "10.000000" : 203,
            "20.000000" : 241,
            "30.000000" : 241,
            "40.000000" : 243,
            "50.000000" : 243,
            "60.000000" : 243,
            "70.000000" : 251,
            "80.000000" : 270,
            "90.000000" : 318,
            "95.000000" : 370,
            "99.000000" : 506,
            "99.500000" : 596,
            "99.900000" : 812,
            "99.950000" : 1032,
            "99.990000" : 2992,
            "0.00" : 0,
            "0.00" : 0,
            "0.00" : 0
          }
        },
        "lat" : {
          "min" : 53,
          "max" : 6330,
          "mean" : 255.56,
          "stddev" : 94.41
        },
        "bw_min" : 15008,
        "bw_max" : 15664,
        "bw_agg" : 100.00,
        "bw_mean" : 15433.60,
        "bw_dev" : 264.57
      },
      "write" : {
        "io_bytes" : 0,
        "bw" : 0,
        "iops" : 0,
        "runtime" : 0,
        "slat" : {
          "min" : 0,
          "max" : 0,
          "mean" : 0.00,
          "stddev" : 0.00
        },
        "clat" : {
          "min" : 0,
          "max" : 0,
          "mean" : 0.00,
          "stddev" : 0.00,
          "percentile" : {
            "1.000000" : 0,
            "5.000000" : 0,
            "10.000000" : 0,
            "20.000000" : 0,
            "30.000000" : 0,
            "40.000000" : 0,
            "50.000000" : 0,
            "60.000000" : 0,
            "70.000000" : 0,
            "80.000000" : 0,
            "90.000000" : 0,
            "95.000000" : 0,
            "99.000000" : 0,
            "99.500000" : 0,
            "99.900000" : 0,
            "99.950000" : 0,
            "99.990000" : 0,
            "0.00" : 0,
            "0.00" : 0,
            "0.00" : 0
          }
        },
        "lat" : {
          "min" : 0,
          "max" : 0,
          "mean" : 0.00,
          "stddev" : 0.00
        },
        "bw_min" : 0,
        "bw_max" : 0,
        "bw_agg" : 0.00,
        "bw_mean" : 0.00,
        "bw_dev" : 0.00
      },
      "trim" : {
        "io_bytes" : 0,
        "bw" : 0,
        "iops" : 0,
        "runtime" : 0,
        "slat" : {
          "min" : 0,
          "max" : 0,
          "mean" : 0.00,
          "stddev" : 0.00
        },
        "clat" : {
          "min" : 0,
          "max" : 0,
          "mean" : 0.00,
          "stddev" : 0.00,
          "percentile" : {
            "1.000000" : 0,
            "5.000000" : 0,
            "10.000000" : 0,
            "20.000000" : 0,
            "30.000000" : 0,
            "40.000000" : 0,
            "50.000000" : 0,
            "60.000000" : 0,
            "70.000000" : 0,
            "80.000000" : 0,
            "90.000000" : 0,
            "95.000000" : 0,
            "99.000000" : 0,
            "99.500000" : 0,
            "99.900000" : 0,
            "99.950000" : 0,
            "99.990000" : 0,
            "0.00" : 0,
            "0.00" : 0,
            "0.00" : 0
          }
        },
        "lat" : {
          "min" : 0,
          "max" : 0,
          "mean" : 0.00,
          "stddev" : 0.00
        },
        "bw_min" : 0,
        "bw_max" : 0,
        "bw_agg" : 0.00,
        "bw_mean" : 0.00,
        "bw_dev" : 0.00
      },
      "usr_cpu" : 0.96,
      "sys_cpu" : 23.82,
      "ctx" : 11122,
      "majf" : 0,
      "minf" : 6,
      "iodepth_level" : {
        "1" : 100.00,
        "2" : 0.00,
        "4" : 0.00,
        "8" : 0.00,
        "16" : 0.00,
        "32" : 0.00,
        ">=64" : 0.00
      },
      "latency_us" : {
        "2" : 0.00,
        "4" : 0.00,
        "10" : 0.00,
        "20" : 0.00,
        "50" : 0.00,
        "100" : 1.31,
        "250" : 67.24,
        "500" : 30.34,
        "750" : 0.94,
        "1000" : 0.12
      },
      "latency_ms" : {
        "2" : 0.03,
        "4" : 0.02,
        "10" : 0.01,
        "20" : 0.00,
        "50" : 0.00,
        "100" : 0.00,
        "250" : 0.00,
        "500" : 0.00,
        "750" : 0.00,
        "1000" : 0.00,
        "2000" : 0.00,
        ">=2000" : 0.00
      },
      "latency_depth" : 2,
      "latency_target" : 0,
      "latency_percentile" : 100.00,
      "latency_window" : 0
    },
    {
      "jobname" : "random-read",
      "groupid" : 0,
      "error" : 0,
      "read" : {
        "io_bytes" : 44992,
        "bw" : 21,
        "iops" : 5,
        "runtime" : 2119748,
        "slat" : {
          "min" : 0,
          "max" : 0,
          "mean" : 0.00,
          "stddev" : 0.00
        },
        "clat" : {
          "min" : 53,
          "max" : 2976,
          "mean" : 254.65,
          "stddev" : 81.49,
          "percentile" : {
            "1.000000" : 79,
            "5.000000" : 181,
            "10.000000" : 195,
            "20.000000" : 241,
            "30.000000" : 241,
            "40.000000" : 243,
            "50.000000" : 243,
            "60.000000" : 243,
            "70.000000" : 251,
            "80.000000" : 270,
            "90.000000" : 318,
            "95.000000" : 374,
            "99.000000" : 510,
            "99.500000" : 564,
            "99.900000" : 972,
            "99.950000" : 1496,
            "99.990000" : 2800,
            "0.00" : 0,
            "0.00" : 0,
            "0.00" : 0
          }
        },
        "lat" : {
          "min" : 53,
          "max" : 2977,
          "mean" : 254.87,
          "stddev" : 81.50
        },
        "bw_min" : 15144,
        "bw_max" : 15704,
        "bw_agg" : 100.00,
        "bw_mean" : 15467.20,
        "bw_dev" : 222.90
      },
      "write" : {
        "io_bytes" : 0,
        "bw" : 0,
        "iops" : 0,
        "runtime" : 0,
        "slat" : {
          "min" : 0,
          "max" : 0,
          "mean" : 0.00,
          "stddev" : 0.00
        },
        "clat" : {
          "min" : 0,
          "max" : 0,
          "mean" : 0.00,
          "stddev" : 0.00,
          "percentile" : {
            "1.000000" : 0,
            "5.000000" : 0,
            "10.000000" : 0,
            "20.000000" : 0,
            "30.000000" : 0,
            "40.000000" : 0,
            "50.000000" : 0,
            "60.000000" : 0,
            "70.000000" : 0,
            "80.000000" : 0,
            "90.000000" : 0,
            "95.000000" : 0,
            "99.000000" : 0,
            "99.500000" : 0,
            "99.900000" : 0,
            "99.950000" : 0,
            "99.990000" : 0,
            "0.00" : 0,
            "0.00" : 0,
            "0.00" : 0
          }
        },
        "lat" : {
          "min" : 0,
          "max" : 0,
          "mean" : 0.00,
          "stddev" : 0.00
        },
        "bw_min" : 0,
        "bw_max" : 0,
        "bw_agg" : 0.00,
        "bw_mean" : 0.00,
        "bw_dev" : 0.00
      },
      "trim" : {
        "io_bytes" : 0,
        "bw" : 0,
        "iops" : 0,
        "runtime" : 0,
        "slat" : {
          "min" : 0,
          "max" : 0,
          "mean" : 0.00,
          "stddev" : 0.00
        },
        "clat" : {
          "min" : 0,
          "max" : 0,
          "mean" : 0.00,
          "stddev" : 0.00,
          "percentile" : {
            "1.000000" : 0,
            "5.000000" : 0,
            "10.000000" : 0,
            "20.000000" : 0,
            "30.000000" : 0,
            "40.000000" : 0,
            "50.000000" : 0,
            "60.000000" : 0,
            "70.000000" : 0,
            "80.000000" : 0,
            "90.000000" : 0,
            "95.000000" : 0,
            "99.000000" : 0,
            "99.500000" : 0,
            "99.900000" : 0,
            "99.950000" : 0,
            "99.990000" : 0,
            "0.00" : 0,
            "0.00" : 0,
            "0.00" : 0
          }
        },
        "lat" : {
          "min" : 0,
          "max" : 0,
          "mean" : 0.00,
          "stddev" : 0.00
        },
        "bw_min" : 0,
        "bw_max" : 0,
        "bw_agg" : 0.00,
        "bw_mean" : 0.00,
        "bw_dev" : 0.00
      },
      "usr_cpu" : 2.07,
      "sys_cpu" : 22.74,
      "ctx" : 11126,
      "majf" : 0,
      "minf" : 7,
      "iodepth_level" : {
        "1" : 100.00,
        "2" : 0.00,
        "4" : 0.00,
        "8" : 0.00,
        "16" : 0.00,
        "32" : 0.00,
        ">=64" : 0.00
      },
      "latency_us" : {
        "2" : 0.00,
        "4" : 0.00,
        "10" : 0.00,
        "20" : 0.00,
        "50" : 0.00,
        "100" : 1.53,
        "250" : 67.31,
        "500" : 30.06,
        "750" : 0.90,
        "1000" : 0.12
      },
      "latency_ms" : {
        "2" : 0.07,
        "4" : 0.02,
        "10" : 0.00,
        "20" : 0.00,
        "50" : 0.00,
        "100" : 0.00,
        "250" : 0.00,
        "500" : 0.00,
        "750" : 0.00,
        "1000" : 0.00,
        "2000" : 0.00,
        ">=2000" : 0.00
      },
      "latency_depth" : 2,
      "latency_target" : 0,
      "latency_percentile" : 100.00,
      "latency_window" : 0
    },
    {
      "jobname" : "random-read",
      "groupid" : 0,
      "error" : 0,
      "read" : {
        "io_bytes" : 45024,
        "bw" : 21,
        "iops" : 5,
        "runtime" : 2114297,
        "slat" : {
          "min" : 0,
          "max" : 0,
          "mean" : 0.00,
          "stddev" : 0.00
        },
        "clat" : {
          "min" : 53,
          "max" : 1752,
          "mean" : 254.25,
          "stddev" : 72.36,
          "percentile" : {
            "1.000000" : 76,
            "5.000000" : 181,
            "10.000000" : 197,
            "20.000000" : 241,
            "30.000000" : 241,
            "40.000000" : 243,
            "50.000000" : 243,
            "60.000000" : 245,
            "70.000000" : 251,
            "80.000000" : 270,
            "90.000000" : 318,
            "95.000000" : 374,
            "99.000000" : 510,
            "99.500000" : 564,
            "99.900000" : 844,
            "99.950000" : 1176,
            "99.990000" : 1720,
            "0.00" : 0,
            "0.00" : 0,
            "0.00" : 0
          }
        },
        "lat" : {
          "min" : 53,
          "max" : 1752,
          "mean" : 254.48,
          "stddev" : 72.40
        },
        "bw_min" : 15320,
        "bw_max" : 15784,
        "bw_agg" : 100.00,
        "bw_mean" : 15504.00,
        "bw_dev" : 191.33
      },
      "write" : {
        "io_bytes" : 0,
        "bw" : 0,
        "iops" : 0,
        "runtime" : 0,
        "slat" : {
          "min" : 0,
          "max" : 0,
          "mean" : 0.00,
          "stddev" : 0.00
        },
        "clat" : {
          "min" : 0,
          "max" : 0,
          "mean" : 0.00,
          "stddev" : 0.00,
          "percentile" : {
            "1.000000" : 0,
            "5.000000" : 0,
            "10.000000" : 0,
            "20.000000" : 0,
            "30.000000" : 0,
            "40.000000" : 0,
            "50.000000" : 0,
            "60.000000" : 0,
            "70.000000" : 0,
            "80.000000" : 0,
            "90.000000" : 0,
            "95.000000" : 0,
            "99.000000" : 0,
            "99.500000" : 0,
            "99.900000" : 0,
            "99.950000" : 0,
            "99.990000" : 0,
            "0.00" : 0,
            "0.00" : 0,
            "0.00" : 0
          }
        },
        "lat" : {
          "min" : 0,
          "max" : 0,
          "mean" : 0.00,
          "stddev" : 0.00
        },
        "bw_min" : 0,
        "bw_max" : 0,
        "bw_agg" : 0.00,
        "bw_mean" : 0.00,
        "bw_dev" : 0.00
      },
      "trim" : {
        "io_bytes" : 0,
        "bw" : 0,
        "iops" : 0,
        "runtime" : 0,
        "slat" : {
          "min" : 0,
          "max" : 0,
          "mean" : 0.00,
          "stddev" : 0.00
        },
        "clat" : {
          "min" : 0,
          "max" : 0,
          "mean" : 0.00,
          "stddev" : 0.00,
          "percentile" : {
            "1.000000" : 0,
            "5.000000" : 0,
            "10.000000" : 0,
            "20.000000" : 0,
            "30.000000" : 0,
            "40.000000" : 0,
            "50.000000" : 0,
            "60.000000" : 0,
            "70.000000" : 0,
            "80.000000" : 0,
            "90.000000" : 0,
            "95.000000" : 0,
            "99.000000" : 0,
            "99.500000" : 0,
            "99.900000" : 0,
            "99.950000" : 0,
            "99.990000" : 0,
            "0.00" : 0,
            "0.00" : 0,
            "0.00" : 0
          }
        },
        "lat" : {
          "min" : 0,
          "max" : 0,
          "mean" : 0.00,
          "stddev" : 0.00
        },
        "bw_min" : 0,
        "bw_max" : 0,
        "bw_agg" : 0.00,
        "bw_mean" : 0.00,
        "bw_dev" : 0.00
      },
      "usr_cpu" : 0.97,
      "sys_cpu" : 23.87,
      "ctx" : 11121,
      "majf" : 0,
      "minf" : 5,
      "iodepth_level" : {
        "1" : 100.00,
        "2" : 0.00,
        "4" : 0.00,
        "8" : 0.00,
        "16" : 0.00,
        "32" : 0.00,
        ">=64" : 0.00
      },
      "latency_us" : {
        "2" : 0.00,
        "4" : 0.00,
        "10" : 0.00,
        "20" : 0.00,
        "50" : 0.00,
        "100" : 1.66,
        "250" : 66.86,
        "500" : 30.38,
        "750" : 0.99,
        "1000" : 0.04
      },
      "latency_ms" : {
        "2" : 0.08,
        "4" : 0.00,
        "10" : 0.00,
        "20" : 0.00,
        "50" : 0.00,
        "100" : 0.00,
        "250" : 0.00,
        "500" : 0.00,
        "750" : 0.00,
        "1000" : 0.00,
        "2000" : 0.00,
        ">=2000" : 0.00
      },
      "latency_depth" : 2,
      "latency_target" : 0,
      "latency_percentile" : 100.00,
      "latency_window" : 0
    },
    {
      "jobname" : "random-read",
      "groupid" : 0,
      "error" : 0,
      "read" : {
        "io_bytes" : 44820,
        "bw" : 21,
        "iops" : 5,
        "runtime" : 2126510,
        "slat" : {
          "min" : 0,
          "max" : 0,
          "mean" : 0.00,
          "stddev" : 0.00
        },
        "clat" : {
          "min" : 53,
          "max" : 5135,
          "mean" : 255.20,
          "stddev" : 85.82,
          "percentile" : {
            "1.000000" : 80,
            "5.000000" : 181,
            "10.000000" : 199,
            "20.000000" : 241,
            "30.000000" : 241,
            "40.000000" : 243,
            "50.000000" : 243,
            "60.000000" : 245,
            "70.000000" : 251,
            "80.000000" : 270,
            "90.000000" : 322,
            "95.000000" : 378,
            "99.000000" : 510,
            "99.500000" : 596,
            "99.900000" : 844,
            "99.950000" : 1208,
            "99.990000" : 1704,
            "0.00" : 0,
            "0.00" : 0,
            "0.00" : 0
          }
        },
        "lat" : {
          "min" : 53,
          "max" : 5136,
          "mean" : 255.42,
          "stddev" : 85.85
        },
        "bw_min" : 15176,
        "bw_max" : 15712,
        "bw_agg" : 100.00,
        "bw_mean" : 15433.60,
        "bw_dev" : 225.52
      },
      "write" : {
        "io_bytes" : 0,
        "bw" : 0,
        "iops" : 0,
        "runtime" : 0,
        "slat" : {
          "min" : 0,
          "max" : 0,
          "mean" : 0.00,
          "stddev" : 0.00
        },
        "clat" : {
          "min" : 0,
          "max" : 0,
          "mean" : 0.00,
          "stddev" : 0.00,
          "percentile" : {
            "1.000000" : 0,
            "5.000000" : 0,
            "10.000000" : 0,
            "20.000000" : 0,
            "30.000000" : 0,
            "40.000000" : 0,
            "50.000000" : 0,
            "60.000000" : 0,
            "70.000000" : 0,
            "80.000000" : 0,
            "90.000000" : 0,
            "95.000000" : 0,
            "99.000000" : 0,
            "99.500000" : 0,
            "99.900000" : 0,
            "99.950000" : 0,
            "99.990000" : 0,
            "0.00" : 0,
            "0.00" : 0,
            "0.00" : 0
          }
        },
        "lat" : {
          "min" : 0,
          "max" : 0,
          "mean" : 0.00,
          "stddev" : 0.00
        },
        "bw_min" : 0,
        "bw_max" : 0,
        "bw_agg" : 0.00,
        "bw_mean" : 0.00,
        "bw_dev" : 0.00
      },
      "trim" : {
        "io_bytes" : 0,
        "bw" : 0,
        "iops" : 0,
        "runtime" : 0,
        "slat" : {
          "min" : 0,
          "max" : 0,
          "mean" : 0.00,
          "stddev" : 0.00
        },
        "clat" : {
          "min" : 0,
          "max" : 0,
          "mean" : 0.00,
          "stddev" : 0.00,
          "percentile" : {
            "1.000000" : 0,
            "5.000000" : 0,
            "10.000000" : 0,
            "20.000000" : 0,
            "30.000000" : 0,
            "40.000000" : 0,
            "50.000000" : 0,
            "60.000000" : 0,
            "70.000000" : 0,
            "80.000000" : 0,
            "90.000000" : 0,
            "95.000000" : 0,
            "99.000000" : 0,
            "99.500000" : 0,
            "99.900000" : 0,
            "99.950000" : 0,
            "99.990000" : 0,
            "0.00" : 0,
            "0.00" : 0,
            "0.00" : 0
          }
        },
        "lat" : {
          "min" : 0,
          "max" : 0,
          "mean" : 0.00,
          "stddev" : 0.00
        },
        "bw_min" : 0,
        "bw_max" : 0,
        "bw_agg" : 0.00,
        "bw_mean" : 0.00,
        "bw_dev" : 0.00
      },
      "usr_cpu" : 1.38,
      "sys_cpu" : 23.47,
      "ctx" : 11076,
      "majf" : 0,
      "minf" : 6,
      "iodepth_level" : {
        "1" : 100.00,
        "2" : 0.00,
        "4" : 0.00,
        "8" : 0.00,
        "16" : 0.00,
        "32" : 0.00,
        ">=64" : 0.00
      },
      "latency_us" : {
        "2" : 0.00,
        "4" : 0.00,
        "10" : 0.00,
        "20" : 0.00,
        "50" : 0.00,
        "100" : 1.53,
        "250" : 67.13,
        "500" : 30.19,
        "750" : 0.98,
        "1000" : 0.11
      },
      "latency_ms" : {
        "2" : 0.05,
        "4" : 0.00,
        "10" : 0.01,
        "20" : 0.00,
        "50" : 0.00,
        "100" : 0.00,
        "250" : 0.00,
        "500" : 0.00,
        "750" : 0.00,
        "1000" : 0.00,
        "2000" : 0.00,
        ">=2000" : 0.00
      },
      "latency_depth" : 2,
      "latency_target" : 0,
      "latency_percentile" : 100.00,
      "latency_window" : 0
    }
  ],
  "disk_util" : [
    {
      "name" : "sda",
      "read_ios" : 44790,
      "write_ios" : 0,
      "read_merges" : 0,
      "write_merges" : 0,
      "read_ticks" : 2712,
      "write_ticks" : 0,
      "in_queue" : 2672,
      "util" : 82.53
    }
  ]
}
"""

    def setUp(self):
        pass

    def test_to_string(self):
        testconv = carbon.converter.JSONToCarbon()
        json_object = json.loads(self.simple_fio_json)
        result = testconv.convert_to_dictionary(json_object, "host.run-name")
        self.assertEqual("7116 1444144664", result["host.run-name.jobs.1.read.io_bytes"], result["host.run-name.jobs.1.read.io_bytes"])

    def test_single_text_element_no_prefix(self):
        testconv = carbon.converter.JSONToCarbon()
        result = testconv.convert_to_dictionary(json.loads(self.single_json_text_element))

        self.assertEqual("value timestamp", result["key"], result["key"])

    def test_single_numeric_element_no_prefix(self):
        testconv = carbon.converter.JSONToCarbon()
        result = testconv.convert_to_dictionary(json.loads(self.single_json_numeric_element))

        self.assertEqual("123 timestamp", result["key"], result["key"])

    def test_single_text_key_space_element_no_prefix(self):
        testconv = carbon.converter.JSONToCarbon()
        result = testconv.convert_to_dictionary(json.loads(self.single_json_key_with_spaces))

        self.assertEqual("value timestamp", result["key_with_spaces"], result["key_with_spaces"])

    def test_single_text_value_space_element_no_prefix(self):
        testconv = carbon.converter.JSONToCarbon()
        result = testconv.convert_to_dictionary(json.loads(self.single_json_value_with_spaces))

        self.assertEqual("value_with_spaces timestamp", result["key"], result["key"])

    def test_map_name_with_space_no_prefix(self):
        testconv = carbon.converter.JSONToCarbon()
        result = testconv.convert_to_dictionary(json.loads(self.json_map_name_with_spaces))

        self.assertEqual("value timestamp", result["map_with_spaces.key"], result["map_with_spaces.key"])

    def test_list_name_with_space_no_prefix(self):
        testconv = carbon.converter.JSONToCarbon()
        result = testconv.convert_to_dictionary(json.loads(self.json_list_name_with_spaces))

        self.assertEqual("value timestamp", result["list_with_spaces.1.key"], result["list_with_spaces.1.key"])


if __name__ == '__main__':
    unittest.main()