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

from builtins import range
from builtins import object
import logging
import platform
import shutil
import subprocess
import time
import appium

from sst import config
from sst.remote_capabilities import SauceLabs

from selenium import webdriver
from selenium.common import exceptions as selenium_exceptions
from selenium.webdriver.common import utils
from selenium.webdriver.firefox import (
    firefox_binary,
    webdriver as ff_webdriver,
)
from selenium.webdriver import ChromeOptions

logger = logging.getLogger('SST')


class BrowserFactory(object):
    """Handle browser creation for tests.

    One instance is used for a given test run.
    """

    webdriver_class = None
    remote_client = None
    creds = None

    def __init__(self):
        super(BrowserFactory, self).__init__()

    def setup_for_test(self, test):
        """Setup the browser for the given test.

        Some browsers accept more options that are test (and browser) specific.

        Daughter classes should redefine this method to capture them.
        """
        pass

    def browser(self):
        """Create a browser based on previously collected options.

        Daughter classes should override this method if they need to provide
        more context.
        """
        return self.webdriver_class()


# MISSINGTEST: Exercise this class -- vila 2013-04-11
class RemoteBrowserFactory(BrowserFactory):

    webdriver_class = webdriver.Remote

    def __init__(self, capabilities, remote_url):
        super(RemoteBrowserFactory, self).__init__()
        if 'saucelabs' in remote_url:
            from sst import runtests
            self.creds = runtests.set_client_credentials('saucelabs')
            try:
                if 'APPIUM_URL' in dir(self.creds):
                    self.browsers = self.creds.CAPABILITIES
                    self.remote_url = self.creds.APPIUM_URL
                    self.webdriver_class = appium.webdriver.Remote
                    apibase = self.creds.API_BASE
                else:
                    self.browsers = self.creds.BROWSERS
                    self.remote_url = self.creds.URL
                    apibase = None

                self.remote_client = SauceLabs(self.creds.USERNAME,
                                               self.creds.ACCESS_KEY,
                                               self.creds.URL,
                                               apibase)

                logger.debug('Connecting to SauceLabs instance: {}'
                             .format(self.remote_url))
            except:
                raise Exception('Please create a sauce_config.py module in '
                                'your test directory with your SauceLabs '
                                'USERNAME, ACCESS_KEY, URL, '
                                'and BROWSERS set.')

        else:
            self.capabilities = capabilities
            self.remote_url = remote_url

    def setup_for_test(self, test):
        if self.webdriver_class == webdriver.Remote:
            self.capabilities = {
                'platform': test.context['platform'],
                'browserName': test.context['browserName'],
                'version': test.context['version'],
                'screenResolution': test.context['screenResolution']
                }
            if 'chromeOptions' in test.context:
                self.capabilities.update({
                    'chromeOptions': test.context['chromeOptions']})
            elif 'moz:firefoxOptions' in test.context:
                self.capabilities.update({
                    'moz:firefoxOptions': test.context['moz:firefoxOptions']})
            self.capabilities['extendedDebugging'] = True
            self.capabilities['idleTimeout'] = 300

        elif self.webdriver_class == appium.webdriver.Remote:
            self.capabilities = {
                'platformName': test.context['platformName'],
                'deviceName': test.context['deviceName'],
                'platformVersion': test.context['platformVersion'],
                'testobject_api_key': test.context['testobject_api_key'],
                'testobject_suite_name': test.context['testobject_suite_name'],
                'testobject_report_results': test.context['testobject_report_results']
                }
            self.capabilities['testobject_test_name'] = test.id()
            self.capabilities['extendedDebugging'] = True
            if 'phoneOnly' in test.context:
                self.capabilities.update(
                    {'phoneOnly': test.context['phoneOnly']})
            if 'deviceOrientation' in test.context:
                self.capabilities.update(
                    {'deviceOrientation': test.context['deviceOrientation']})
            if 'newCommandTimeout' in test.context:
                self.capabilities.update(
                    {'newCommandTimeout': test.context['newCommandTimeout']})
        logger.debug('Remote capabilities set: {}'.format(self.capabilities))

    def browser(self):
        return self.webdriver_class(self.remote_url, self.capabilities)


# MISSINGTEST: Exercise this class -- vila 2013-04-11
class ChromeFactory(BrowserFactory):

    webdriver_class = webdriver.Chrome

    def setup_for_test(self, test):
        chrome_options = ChromeOptions()
        chrome_options.add_argument("test-type")
        chrome_options.add_argument("disable-infobars")
        chrome_options.add_experimental_option('prefs', {
            'credentials_enable_service': False,
            'profile.password_manager_enabled': False,
            'profile.default_content_setting_values.plugins': 1,
            'profile.content_settings.plugin_whitelist.adobe-flash-player': 1,
            'profile.content_settings.exceptions.plugins.*,*.per_resource.adobe-flash-player': 1
        })

        if test.use_proxy:
            chrome_options.add_argument("--proxy-server={0}".format(test.proxy_address))
        self.capabilities = chrome_options.to_capabilities()
        logger.debug("Chrome capabilities: {}".format(self.capabilities))

    def browser(self):
        return self.webdriver_class(desired_capabilities=self.capabilities)


class SafariFactory(BrowserFactory):

    webdriver_class = webdriver.Safari

    def setup_for_test(self, test):
        self.capabilities = webdriver.safari.webdriver.DesiredCapabilities.SAFARI
        logger.debug("Safari capabilities: {}".format(self.capabilities))

    def browser(self):
        return self.webdriver_class(desired_capabilities=self.capabilities)


class AppiumFactory(BrowserFactory):

    webdriver_class = appium.webdriver.Remote

    def setup_for_test(self, test):
        from sst import runtests
        self.creds = runtests.set_client_credentials('appium')
        self.server, self.caps = self.creds.SERVER, self.creds.CAPABILITIES
        logger.debug("Appium capabilities: {}".format(self.caps))

    def browser(self):
        return self.webdriver_class(self.server, self.caps)


# MISSINGTEST: Exercise this class (requires windows) -- vila 2013-04-11
class IeFactory(BrowserFactory):

    webdriver_class = webdriver.Ie


# MISSINGTEST: Exercise this class -- vila 2013-04-11
class PhantomJSFactory(BrowserFactory):

    webdriver_class = webdriver.PhantomJS


# MISSINGTEST: Exercise this class -- vila 2013-04-11
class OperaFactory(BrowserFactory):

    webdriver_class = webdriver.Opera


class FirefoxBinary(firefox_binary.FirefoxBinary):
    """Workarounds selenium firefox issues.

    There is race condition in the way firefox is spawned. The exact cause
    hasn't been properly diagnosed yet but it's around:

    - getting a free port from the OS with selenium.webdriver.common.utils
      free_port(),

    - release the port immediately but record it in ff prefs so that ff can
      listen on that port for the internal http server.

    It has been observed that this leads to hanging processes for 'firefox
    -silent'.
    """

    def _start_from_profile_path(self, path):
        self._firefox_env["XRE_PROFILE_PATH"] = path

        if platform.system().lower() == 'linux':
            self._modify_link_library_path()
        command = [self._start_cmd, "-silent"]
        if self.command_line is not None:
            for cli in self.command_line:
                command.append(cli)

# The following exists upstream and is known to create hanging firefoxes,
# leading to zombies.
#        out, _ = Popen(command, stdout=PIPE, stderr=STDOUT,
#                       env=self._firefox_env).communicate()
#        logger.debug('firefox -silent returned: %s' % (out,))
        command[1] = '-foreground'
        self.process = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            env=self._firefox_env)

    def _wait_until_connectable(self, **kwargs):
        """Blocks until the extension is connectable in the firefox.

        The base class implements this by checking utils.is_connectable() every
        second (sleep_for == 1) and failing after 30 attempts (max_tries ==
        30). Expriments showed that once a firefox can't be connected to, it's
        better to start a new one instead so we don't wait 30 seconds to fail
        in the end (the caller should catch WebDriverException and starts a new
        firefox).
        """
        connectable = False
        max_tries = 10
        sleep_for = 1
        for count in range(1, max_tries):
            connectable = utils.is_connectable(self.profile.port)
            if connectable:
                break
            logger.debug('Cannot connect to process %d with port: %d, count %d'
                         % (self.process.pid, self.profile.port, count))
            if self.process.poll() is not None:
                # Browser has exited
                raise selenium_exceptions.WebDriverException(
                    "The browser appears to have exited "
                    "before we could connect. If you specified a log_file in "
                    "the FirefoxBinary constructor, check it for details.")
            time.sleep(sleep_for)
        if not connectable:
            self.kill()
            raise selenium_exceptions.WebDriverException(
                "Cannot connect to the selenium extension. If you specified a "
                "log_file in the FirefoxBinary constructor, check it for "
                "details.")
        return connectable


class WebDriverFirefox(ff_webdriver.WebDriver):
    """Workarounds selenium firefox issues."""

    def __init__(self, firefox_profile=None, firefox_binary=None, timeout=30,
                 capabilities=None, proxy=None):
        try:
            super(WebDriverFirefox, self).__init__(
                firefox_profile, FirefoxBinary(), timeout, capabilities, proxy)
        except selenium_exceptions.WebDriverException:
            # If we can't start, cleanup profile
            shutil.rmtree(self.profile.path)
            if self.profile.tempfolder is not None:
                shutil.rmtree(self.profile.tempfolder)
            raise


class FirefoxFactory(BrowserFactory):

    webdriver_class = WebDriverFirefox

    def setup_for_test(self, test):
        profile = webdriver.FirefoxProfile()
        profile.set_preference('media.gmp-manager.updateEnabled', True)
        profile.set_preference('intl.accept_languages', 'en')
        profile.set_preference('browser.download.folderList', 1)
        profile.set_preference('browser.download.manager.showWhenStarting', False)
        profile.set_preference('browser.download.manager.useWindow', False)
        profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'text/csv')
        profile.set_preference('reader.parse-on-load.enabled', False)
        profile.set_preference('network.http.response.timeout', 60)
        if test.assume_trusted_cert_issuer:
            profile.set_preference('webdriver_assume_untrusted_issuer', False)
            profile.set_preference(
                'capability.policy.default.Window.QueryInterface', 'allAccess')
            profile.set_preference(
                'capability.policy.default.Window.frameElement.get',
                'allAccess')
        self.profile = profile

    def browser(self):
        return self.webdriver_class(self.profile)


# MISSINGTEST: Exercise this class -- vila 2013-04-11
browser_factories = {
    'Chrome': ChromeFactory,
    'Firefox': FirefoxFactory,
    'Safari': SafariFactory,
    'Ie': IeFactory,
    'Opera': OperaFactory,
    'PhantomJS': PhantomJSFactory,
    'Appium': AppiumFactory
}
