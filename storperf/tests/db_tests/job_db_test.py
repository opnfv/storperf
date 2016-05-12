##############################################################################
# Copyright (c) 2016 EMC and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

from storperf.db.job_db import JobDB
from storperf.workloads.rr import rr
import os
import sqlite3
import unittest

import mock


class JobDBTest(unittest.TestCase):

    def setUp(self):

        JobDB.db_name = __name__ + '.db'
        try:
            os.remove(JobDB.db_name)
        except OSError:
            pass
        self.job = JobDB()

    @mock.patch("uuid.uuid4")
    def test_create_job(self, mock_uuid):
        expected = "ABCDE-12345"
        mock_uuid.side_effect = (expected,)

        self.job.create_job_id()

        actual = self.job.job_id

        self.assertEqual(
            expected, actual, "Did not expect: " + str(actual))

    @mock.patch("uuid.uuid4")
    def test_duplicate_job_generated(self, mock_uuid):
        duplicate = "EDCBA-12345"
        expected = "EDCBA-54321"

        mock_uuid.side_effect = (duplicate, duplicate, expected,)

        self.job.create_job_id()
        self.job.create_job_id()

        actual = self.job.job_id

        self.assertEqual(
            expected, actual, "Did not expect: " + str(actual))

    @mock.patch("uuid.uuid4")
    @mock.patch("calendar.timegm")
    def test_start_job(self, mock_calendar, mock_uuid):
        job_id = "ABCDE-12345"
        start_time = "12345"
        mock_calendar.side_effect = (start_time,)
        mock_uuid.side_effect = (job_id,)
        workload = rr()

        db = sqlite3.connect(JobDB.db_name)
        cursor = db.cursor()

        row = cursor.execute(
            """select * from jobs
                       where job_id = ?
                       and workload = ?""",
            (job_id, workload.fullname,))

        self.assertEqual(None,
                         row.fetchone(),
                         "Should not have been a row in the db")

        self.job.start_workload(workload)

        cursor.execute(
            """select job_id, workload, start from jobs
                       where job_id = ?
                       and workload = ?""",
            (job_id, workload.fullname,))

        row = cursor.fetchone()

        self.assertNotEqual(None, row, "Should be a row in the db")
        self.assertEqual(job_id, row[0], "Did not expect " + str(row[0]))
        self.assertEqual(
            workload.fullname, row[1], "Did not expect " + str(row[1]))
        self.assertEqual(start_time, row[2], "Did not expect " + str(row[2]))

    @mock.patch("uuid.uuid4")
    @mock.patch("calendar.timegm")
    def test_end_job(self, mock_calendar, mock_uuid):
        job_id = "ABCDE-12345"
        start_time = "12345"
        end_time = "54321"
        mock_calendar.side_effect = (start_time, end_time,)
        mock_uuid.side_effect = (job_id,)
        workload = rr()

        self.job.start_workload(workload)
        self.job.end_workload(workload)

        db = sqlite3.connect(JobDB.db_name)
        cursor = db.cursor()
        cursor.execute(
            """select job_id, workload, start, end from jobs
                       where job_id = ?
                       and workload = ?""",
            (job_id, workload.fullname,))

        row = cursor.fetchone()

        self.assertNotEqual(None, row, "Should be a row in the db")
        self.assertEqual(job_id, row[0], "Did not expect " + str(row[0]))
        self.assertEqual(
            workload.fullname, row[1], "Did not expect " + str(row[1]))
        self.assertEqual(start_time, row[2], "Did not expect " + str(row[2]))
        self.assertEqual(end_time, row[3], "Did not expect " + str(row[3]))

    @mock.patch("uuid.uuid4")
    @mock.patch("calendar.timegm")
    def test_duplicate_start_job(self, mock_calendar, mock_uuid):
        job_id = "ABCDE-12345"
        start_time_1 = "12345"
        start_time_2 = "12346"

        mock_calendar.side_effect = (start_time_1, start_time_2)
        mock_uuid.side_effect = (job_id,)
        workload = rr()

        db = sqlite3.connect(JobDB.db_name)
        cursor = db.cursor()

        self.job.start_workload(workload)
        self.job.start_workload(workload)

        cursor.execute(
            """select job_id, workload, start from jobs
                       where job_id = ?
                       and workload = ?""",
            (job_id, workload.fullname,))

        row = cursor.fetchone()

        self.assertNotEqual(None, row, "Should be a row in the db")
        self.assertEqual(job_id, row[0], "Did not expect " + str(row[0]))
        self.assertEqual(
            workload.fullname, row[1], "Did not expect " + str(row[1]))
        self.assertEqual(start_time_2, row[2], "Did not expect " + str(row[2]))

    @mock.patch("uuid.uuid4")
    @mock.patch("calendar.timegm")
    def test_end_job_without_start(self, mock_calendar, mock_uuid):
        job_id = "ABCDE-12345"
        start_time = "12345"
        end_time = "54321"
        mock_calendar.side_effect = (start_time, end_time,)
        mock_uuid.side_effect = (job_id,)
        workload = rr()

        self.job.end_workload(workload)

        db = sqlite3.connect(JobDB.db_name)
        cursor = db.cursor()
        cursor.execute(
            """select job_id, workload, start, end from jobs
                       where job_id = ?
                       and workload = ?""",
            (job_id, workload.fullname,))

        row = cursor.fetchone()

        self.assertNotEqual(None, row, "Should be a row in the db")
        self.assertEqual(job_id, row[0], "Did not expect " + str(row[0]))
        self.assertEqual(
            workload.fullname, row[1], "Did not expect " + str(row[1]))
        # The start time is set to the same time as end if it was never set
        # before
        self.assertEqual(start_time, row[2], "Did not expect " + str(row[2]))
        self.assertEqual(start_time, row[3], "Did not expect " + str(row[3]))

    def test_job_params(self):
        expected = {"a": "1", "b": "2"}
        self.job.job_id = "ABCD"
        self.job.record_workload_params(expected)
        actual = self.job.fetch_workload_params(self.job.job_id)
        self.assertEqual(expected, actual)
