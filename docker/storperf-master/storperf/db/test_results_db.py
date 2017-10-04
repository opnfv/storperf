##############################################################################
# Copyright (c) 2016 EMC and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

import json
import requests


def push_results_to_db(db_url, details, logger):
    """
    POST results to the Result target DB
    """
    url = db_url + "/results"

    headers = {'Content-Type': 'application/json'}
    try:
        if logger:
            jsonified_params = json.dumps(details)
            logger.info("Pushing results to %s" % (url))
            logger.debug("Parameters: %s" % details)
        r = requests.post(url, data=jsonified_params, headers=headers)
        if logger:
            logger.debug(r)
            logger.debug(r.status_code)
            logger.debug(r.content)
        return json.loads(r.content)
    except Exception:
        if logger:
            logger.exception("Error [push_results_to_db('%s', '%s')]:" %
                             (db_url, details))
        return None
