##############################################################################
# Copyright (c) 2016 EMC and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

import json
import os
import requests


def get_installer_type(logger=None):
    """
    Get installer type (fuel, apex, joid, compass)
    """
    try:
        installer = os.environ['INSTALLER_TYPE']
    except KeyError:
        if logger:
            logger.error("Impossible to retrieve the installer type")
        installer = "Unknown_installer"

    return installer


def push_results_to_db(db_url, project, case_name,
                       test_start, test_stop, logger, pod_name,
                       version, scenario, criteria, build_tag, details):
    """
    POST results to the Result target DB
    """
    url = db_url + "/results"
    installer = get_installer_type(logger)

    params = {"project_name": project, "case_name": case_name,
              "pod_name": pod_name, "installer": installer,
              "version": version, "scenario": scenario, "criteria": criteria,
              "build_tag": build_tag, "start_date": test_start,
              "stop_date": test_stop, "details": details}

    headers = {'Content-Type': 'application/json'}
    try:
        if logger:
            jsonified_params = json.dumps(params)
            logger.info("Pushing results to %s" % (url))
            logger.debug("Parameters: %s" % jsonified_params[:1024])
        r = requests.post(url, data=jsonified_params, headers=headers)
        if logger:
            logger.debug(r)
            logger.debug(r.status_code)
            logger.debug(r.content)
        return True
    except Exception, e:
        logger.error("Error [push_results_to_db('%s', '%s', '%s', " +
                     "'%s', '%s', '%s', '%s', '%s', '%s')]:" %
                     (db_url, project, case_name, pod_name, version,
                      scenario, criteria, build_tag, details), e)
        return False
