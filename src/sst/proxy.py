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

import os
import json
import logging
import requests

from browsermobproxy import Server

dirname = os.path.dirname
BMP_PATH = 'browsermob-proxy-2.1.1/bin/browsermob-proxy'
BMP_BIN = os.path.join(dirname(__file__), BMP_PATH)

logger = logging.getLogger('SST')

class Proxy(object):

        API = 'http://localhost:8080/proxy/'

        proxy = None
        proxy_server = None
        test_id = None

        blacklist = ['micpn.com', 'switchads.com', 'mathtag.com', 'adnxs.com',
                   'bidswitch.net', 'clicktale.net', 'casalemedia.com',
                   'pubmatic.com', 'switchadhub.com', 'contextweb.com',
                   'adsrvr.org', 'dpclk.com', 'rubiconproject.com',
                   'doubleclick.net', 'rfihub.com', 'quantserve.com',
                   'advertising.com', 'tidaltv.com', 'moatads.com',
                   'adform.net', 'turn.com', 'chango.com', 'nr-data.net']

        def __init__(self, test_id):
            self.test_id = test_id
            self.start_proxy()

        def start_proxy(self):
            self.proxy_server = Server(BMP_BIN)
            self.proxy_server.start()
            self.proxy = self.proxy_server.create_proxy()
            self.set_blacklist()
            self.proxy.new_har(self.test_id)
            logger.debug('Browsermob proxy started.')
            return self

        def stop_proxy(self):
            filename = '{}.har'.format(self.test_id)
            with open(filename, 'w') as harfile:
                json.dump(self.proxy.har, harfile)
            data = json.dumps(self.proxy.har, ensure_ascii=False)
            # logger.debug('Dumping HAR')
            # logger.debug(data)
            self.proxy_server.stop()
            logger.debug('Browsermob proxy stopped. HAR created: {}'.format(filename))

        def set_blacklist(self):
            for domain in self.blacklist:
                self.proxy.blacklist("^https?://([a-z0-9-]+[.])*{}*.*".format(domain), 404)

            logger.debug("Proxy blacklist set.")
            # blacklisted = requests.get('{}{}/blacklist'.format(self.API, self.proxy.port))
            # logger.debug('Blacklisted: \n{}'.format(blacklisted.text))
