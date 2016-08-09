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

class SauceLabs(object):
    capabilities = {'browserName': 'chrome', 'platform': 'Windows 7',
                    'version': '51.0', 'screenResolution': '1920x1200'}

class BrowserStack(object):
    capabilities = {'browser': 'Chrome', 'browser_version': '52.0',
                    'os': 'Windows', 'os_version': '7',
                    'resolution': '1920x1080',
                    'browserstack.debug': True,
                    'chromeOptions': {'args': '--disable-extensions'}}
