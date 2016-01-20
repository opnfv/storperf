##############################################################################
# Copyright (c) 2015 EMC and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

from _sqlite3 import OperationalError
import calendar
import logging
import sqlite3
import time
import uuid

import requests


class JobDB(object):

    db_name = "StorPerf.db"

    def __init__(self):
        """
        Creates the StorPerf.db and jobs tables on demand
        """

        self.logger = logging.getLogger(__name__)
        self.logger.debug("Connecting to " + JobDB.db_name)
        self.job_id = None

        db = sqlite3.connect(JobDB.db_name)
        cursor = db.cursor()
        try:
            cursor.execute('''CREATE TABLE jobs
            (job_id text,
            workload text,
            start text,
            end text)''')
            self.logger.debug("Created job table")
        except OperationalError:
            self.logger.debug("Job table exists")

        cursor.execute('SELECT * FROM jobs')

    def create_job_id(self):
        """
        Returns a job id that is guaranteed to be unique in this
        StorPerf instance.
        """
        db = sqlite3.connect(JobDB.db_name)
        cursor = db.cursor()

        self.job_id = str(uuid.uuid4())
        row = cursor.execute(
            "select * from jobs where job_id = ?", (self.job_id,))

        while (row.fetchone() is not None):
            self.logger.info("Duplicate job id found, regenerating")
            self.job_id = str(uuid.uuid4())
            row = cursor.execute(
                "select * from jobs where job_id = ?", (self.job_id,))

        cursor.execute(
            "insert into jobs(job_id) values (?)", (self.job_id,))
        self.logger.debug("Reserved job id " + self.job_id)
        db.commit()

    def start_workload(self, workload_name):
        """
        Records the start time for the given workload
        """
        if (self.job_id is None):
            self.create_job_id()

        db = sqlite3.connect(JobDB.db_name)
        cursor = db.cursor()

        now = str(calendar.timegm(time.gmtime()))

        row = cursor.execute(
            """select * from jobs
                       where job_id = ?
                       and workload = ?""",
            (self.job_id, workload_name,))

        if (row.fetchone() is None):
            cursor.execute(
                """insert into jobs
                           (job_id,
                           workload,
                           start)
                           values (?, ?, ?)""",
                (self.job_id,
                 workload_name,
                 now,))
        else:
            self.logger.warn("Duplicate start time for workload "
                             + workload_name)
            cursor.execute(
                """update jobs set
                           job_id = ?,
                           start = ?
                           where workload = ?""",
                (self.job_id,
                 now,
                 workload_name,))

        db.commit()

    def end_workload(self, workload_name):
        """
        Records the end time for the given workload
        """
        if (self.job_id is None):
            self.create_job_id()

        db = sqlite3.connect(JobDB.db_name)
        cursor = db.cursor()
        now = str(calendar.timegm(time.gmtime()))

        row = cursor.execute(
            """select * from jobs
                       where job_id = ?
                       and workload = ?""",
            (self.job_id, workload_name,))

        if (row.fetchone() is None):
            self.logger.warn("No start time recorded for workload "
                             + workload_name)
            cursor.execute(
                """insert into jobs
                           (job_id,
                           workload,
                           start,
                           end)
                           values (?, ?, ?, ?)""",
                (self.job_id,
                 workload_name,
                 now,
                 now))
        else:
            cursor.execute(
                """update jobs set
                           job_id = ?,
                           end = ?
                           where workload = ?""",
                (self.job_id,
                 now,
                 workload_name,))

        db.commit()

    def fetch_results(self, workload_prefix=""):
        if (workload_prefix is None):
            workload_prefix = ""

        workload_prefix = workload_prefix + "%"

        stats = ()

        start_time = str(calendar.timegm(time.gmtime()))
        end_time = "0"

        self.logger.debug("Workload like: " + workload_prefix)

        db = sqlite3.connect(JobDB.db_name)
        cursor = db.cursor()
        cursor.execute("""select start, end, workload
            from jobs where workload like ?""",
                       (workload_prefix,))

        while (True):
            row = cursor.fetchone()
            if (row is None):
                break

            start_time = str(row[0])
            end_time = str(row[1])
            workload = str(row[2])

            # for most of these stats, we just want the final one
            # as that is cumulative average or whatever for the whole
            # run

            self.logger.info("workload=" + workload +
                             "start=" + start_time + " end=" + end_time)

            request = 'http://127.0.0.1:8000/render/?target=*.' + self.job_id + \
                '.' + workload + '.jobs.1.*.clat.mean&format=json&from=' + \
                start_time + "&until=" + end_time

            response = requests.get(request)

            if (response.status_code == 200):
                data = response.json()
                print data
            else:
                pass
