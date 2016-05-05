##############################################################################
# Copyright (c) 2015 EMC and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

from sqlite3 import OperationalError
from threading import Lock
import calendar
import logging
import sqlite3
import time
import uuid


db_mutex = Lock()


class JobDB(object):

    db_name = "StorPerfJob.db"

    def __init__(self):
        """
        Creates the StorPerfJob.db and jobs tables on demand
        """

        self.logger = logging.getLogger(__name__)
        self.logger.debug("Connecting to " + JobDB.db_name)
        self.job_id = None

        with db_mutex:
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
            db.commit()
            db.close()

    def create_job_id(self):
        """
        Returns a job id that is guaranteed to be unique in this
        StorPerf instance.
        """
        with db_mutex:
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
            db.close()

    def start_workload(self, workload):
        """
        Records the start time for the given workload
        """

        workload_name = workload.fullname

        if (self.job_id is None):
            self.create_job_id()

        with db_mutex:

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
                self.logger.warn("Duplicate start time for workload %s"
                                 % workload_name)
                cursor.execute(
                    """update jobs set
                               job_id = ?,
                               start = ?
                               where workload = ?""",
                    (self.job_id,
                     now,
                     workload_name,))

            db.commit()
            db.close()

    def end_workload(self, workload):
        """
        Records the end time for the given workload
        """
        if (self.job_id is None):
            self.create_job_id()

        workload_name = workload.fullname

        with db_mutex:

            db = sqlite3.connect(JobDB.db_name)
            cursor = db.cursor()
            now = str(calendar.timegm(time.gmtime()))

            row = cursor.execute(
                """select * from jobs
                           where job_id = ?
                           and workload = ?""",
                (self.job_id, workload_name,))

            if (row.fetchone() is None):
                self.logger.warn("No start time recorded for workload %s"
                                 % workload_name)
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
            db.close()

    def fetch_workloads(self, workload):
        workload_prefix = workload + "%"
        workload_executions = []

        with db_mutex:
            db = sqlite3.connect(JobDB.db_name)
            cursor = db.cursor()
            cursor.execute("""select  workload, start, end
                from jobs where workload like ?""",
                           (workload_prefix,))

            while (True):
                row = cursor.fetchone()
                if (row is None):
                    break
                workload_execution = [row[0], row[1], row[2]]
                workload_executions.append(workload_execution)
            db.close()

        return workload_executions
