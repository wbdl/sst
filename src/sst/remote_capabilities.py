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
    client = None
    USERNAME = 'rmdaggett'
    ACCESS_KEY = '5e95db45-67e7-46a6-b95d-79cb68bb2ff0'
    URL = 'http://{}:{}@ondemand.saucelabs.com:80/wd/hub'.format(USERNAME, ACCESS_KEY)
    results = []
    capabilities = {'browserName': 'chrome', 'platform': 'Windows 7',
                    'version': '52.0', 'screenResolution': '1920x1200'}

    def __init__(self):
        logger.debug('Creating sauceclient')
        self.client = sauceclient.SauceClient(self.USERNAME, self.ACCESS_KEY,)

    def send_result(self, session_id, name, result):
        self.client.jobs.update_job(job_id=session_id, name=name, passed=result)

class BrowserStack(object):
    USERNAME = 'ryandaggett1'
    ACCESS_KEY = 'jeP4x8qypqsa3PYZabRd'
    URL = 'http://{}:{}@hub.browserstack.com:80/wd/hub'.format(USERNAME, ACCESS_KEY)
    results = []
    capabilities = {'browser': 'Chrome', 'browser_version': '52.0',
                    'os': 'Windows', 'os_version': '7',
                    'resolution': '1920x1080',
                    'browserstack.debug': True,
                    'chromeOptions': {'args': '--disable-extensions'}}

    def __init__(self):
        logger.debug('Creating BrowserStack client')

    def send_result(self, session_id, result):
        status = "completed" if result else "error"
        requests.put('https://ryandaggett2:1PJNUhQkZyqfgECzPuPy@www.browserstack.com/automate/sessions/{}.json'.format(session_id), data={"status": status, "reason": ""})