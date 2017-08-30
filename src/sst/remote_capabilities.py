#
#   Copyright (c) 2011-2013 Canonical Ltd.
#
#   This file is part of: SST (selenium-simple-test)
#   https://launchpad.net/selenium-simple-test
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

import logging
import requests
import sauceclient

logger = logging.getLogger('SST')


class SauceLabs(object):
    """Helper class for creating an instance of sauceclient and posting results.
    Credentials should be defined in the directory where your tests
    are stored in a sauce_config.py module."""

    client = None
    URL = None

    def __init__(self, username, access_key, url):
        logger.debug('Creating SauceLabs client')
        self.URL = url
        self.client = sauceclient.SauceClient(username, access_key,)

    def send_result(self, session_id, name, result):
        logger.debug('Sending result to SauceLabs')
        print('SauceOnDemandSessionID={} job-name={}'.format(session_id,
                                                             name))
        self.client.jobs.update_job(job_id=session_id, name=name,
                                    passed=result)
