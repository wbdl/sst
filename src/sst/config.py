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

"""
The `sst.config` module has the following information::

    from sst import config

    # which browser is being used?
    config.browser_type

    # full path to the shared directory
    config.shared_directory

    # full path to the results directory
    config.results_directory

    # flags for the current test run
    config.flags

    # A per test cache. A dictionary that is cleared at the start of each test.
    config.cache

    # path to the browsermob proxy binary
    config.proxy_bin

    # proxy API address
    config.proxy_api

    # domains to add to the browsermob proxy blacklist
    config.blacklist
"""
import os

browser_type = None
_current_context = None
shared_directory = None
results_directory = None
api_test_results = None
api_client = None
flags = []
__args__ = {}
cache = {}

# Browsermob proxy settings
dirname = os.path.dirname
bmp_path= 'browsermob-proxy-2.1.4/bin/browsermob-proxy'
proxy_bin = os.path.join(dirname(__file__), bmp_path)
proxy_api = 'http://localhost:8080/proxy/'
blacklist = ['micpn.com', 'switchads.com', 'mathtag.com', 'adnxs.com',
           'bidswitch.net', 'clicktale.net', 'casalemedia.com',
           'pubmatic.com', 'switchadhub.com', 'contextweb.com',
           'adsrvr.org', 'dpclk.com', 'rubiconproject.com',
           'doubleclick.net', 'rfihub.com', 'quantserve.com',
           'advertising.com', 'tidaltv.com', 'moatads.com',
           'adform.net', 'turn.com', 'chango.com', 'nr-data.net', 'adroll.com',
           'mediaforge.com', 'linksynergy.com', 'adtechus.comovie', 'criteo.net',
           'openx.net', 'bluekai.com', 'bkrtx.com', 'indexww.com', 'simpli.fi']
