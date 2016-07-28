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

import json
import logging
import requests

from sst import config
from browsermobproxy import Server

logger = logging.getLogger('SST')

class Proxy(object):

        proxy = None
        proxy_server = None
        test_id = None

        def __init__(self, test_id):
            self.test_id = test_id
            self.start_proxy()

        def start_proxy(self):
            self.proxy_server = Server(config.proxy_bin)
            self.proxy_server.start()
            self.proxy = self.proxy_server.create_proxy()
            if config.blacklist:
                self.set_blacklist(config.blacklist)
            self.proxy.new_har(self.test_id)
            logger.debug('Browsermob proxy started.')
            return self

        def stop_proxy(self):
            filename = '{}.har'.format(self.test_id)
            with open(filename, 'w') as harfile:
                json.dump(self.proxy.har, harfile)
            data = json.dumps(self.proxy.har, ensure_ascii=False)
            self.proxy_server.stop()
            logger.debug('Browsermob proxy stopped. HAR created: {}'.format(filename))

        def set_blacklist(self, domain_list):
            for domain in domain_list:
                self.proxy.blacklist("^https?://([a-z0-9-]+[.])*{}*.*".format(domain), 404)
            logger.debug("Proxy blacklist set.")

        def get_blacklist(self):
            return requests.get('{}{}/blacklist'.format(config.proxy_api, self.proxy.port))
