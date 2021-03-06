#
#   Copyright (c) 2011,2012,2013 Canonical Ltd.
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

from __future__ import absolute_import

import imp
import junitxml
import logging
import os
import sys

import testtools

from collections import OrderedDict
from .testrail_api import *
from sst import (
    browsers,
    cases,
    concurrency,
    config,
    filters,
    loaders,
    results,
    remote_capabilities,
    testrail_helper
)

# Maintaining compatibility until we deprecate the followings
BrowserFactory = browsers.BrowserFactory
RemoteBrowserFactory = browsers.RemoteBrowserFactory
ChromeFactory = browsers.ChromeFactory
IeFactory = browsers.IeFactory
PhantomJSFactory = browsers.PhantomJSFactory
OperaFactory = browsers.OperaFactory
FirefoxFactory = browsers.FirefoxFactory
browser_factories = browsers.browser_factories
SSTTestCase = cases.SSTTestCase
SSTScriptTestCase = cases.SSTScriptTestCase


__all__ = ('runtests')

logger = logging.getLogger('SST')


# MISSINGTEST: 'shared' relationship with test_dir, auto-added to sys.path or
# not -- vila 2013-05-05
def runtests(test_regexps, results_directory, out,
             test_dir='.', collect_only=False,
             browser_factory=None,
             report_format='console',
             shared_directory=None,
             screenshots_on=False,
             concurrency_num=1,
             failfast=False,
             debug=False,
             extended=False,
             includes=None,
             excludes=None,
             api_test_results=None,
             use_proxy=False):
    if not os.path.isdir(test_dir):
        raise RuntimeError('Specified directory %r does not exist'
                           % (test_dir,))
    if browser_factory is None and collect_only is False:
        raise RuntimeError('A browser must be specified')
    shared_directory = find_shared_directory(test_dir, shared_directory)
    config.shared_directory = shared_directory
    if shared_directory is not None:
        sys.path.append(shared_directory)

    loader = loaders.SSTestLoader(results_directory,
                                  browser_factory, screenshots_on,
                                  debug, extended, use_proxy)
    alltests = loader.suiteClass()
    alltests.addTests(loader.discoverTestsFromTree(test_dir))
    alltests = filters.include_regexps(test_regexps, alltests)
    alltests = filters.exclude_regexps(excludes, alltests)
    if config.api_test_results:
        set_client_credentials('testrail')
        client = config.api_client
        if browser_factory.remote_client:
            if config.api_test_results == True:
                client.create_test_plan()
                for browser in browser_factory.browsers:
                    tests = [t.case_id for t in alltests._tests if t.case_id]
                    ids = list(OrderedDict.fromkeys(tests))
                    # web
                    if 'browserName' in browser.keys():
                        platform = 'platform'
                        version = 'version'
                        name = 'browserName'
                    # app
                    else:
                        platform = 'platformName'
                        version = 'platformVersion'
                        name = 'deviceName'
                    platform_string = '{} - {} - {}'.format(
                        browser[platform],
                        browser[name],
                        browser[version])
                    test_run = client.create_test_run(ids, platform_string)
                    logger.debug('Cases in current run ({} {}:{}): {}'.format(
                                  browser[name],
                                  browser[version],
                                  test_run['run_id'],
                                  ids))
                    for test in alltests._tests:
                        if browser == test.context:
                            test.run_id = test_run['run_id']
                logger.debug('Created test runs {} using the above cases'
                                .format(client.runs))

            elif type(config.api_test_results) == int:
                plan_id = config.api_test_results
                runs_list = client.get_runs_in_plan(plan_id)
                existing_runs = []
                for browser in browser_factory.browsers:
                    # web
                    if 'browserName' in browser.keys():
                        platform = 'platform'
                        version = 'version'
                        name = 'browserName'
                    # app
                    else:
                        platform = 'platformName'
                        version = 'platformVersion'
                        name = 'deviceName'
                    platform_string = '{} {}, {}'.format(
                        browser[name].lower(),
                        browser[version].split('.')[0],
                        browser[platform].lower())
                    run_found = False
                    for test_run in runs_list:
                        if test_run['config']:
                            run_config = test_run['config'].lower()
                        else:
                            run_config = test_run['name'].lower()
                        if platform_string == run_config:
                            run_found = True
                            existing_runs.append(test_run)
                            logger.debug("Found existing run for {}".format(platform_string))
                    if not run_found:
                        logger.debug("Could not find existing test run of matching capabilities: {}".format(platform_string))
                        # TODO create new test run within the provided plan ID
                        #logger.debug("Creating new test run in plan {}".format(plan_id))
                        # client.create_test_run(ids, platform_string)
                # add run_id to individual tests
                for test_run in existing_runs:
                    for test in alltests._tests:
                        # web
                        if 'browserName' in test.context.keys():
                            platform = 'platform'
                            version = 'version'
                            name = 'browserName'
                        # app
                        else:
                            platform = 'platformName'
                            version = 'platformVersion'
                            name = 'deviceName'
                        test_context = '{} {}, {}'.format(
                            test.context[name].lower(),
                            test.context[version].split('.')[0],
                            test.context[platform].lower())
                        if test_run['config']:
                            run_config = test_run['config'].lower()
                        else:
                            run_config = test_run['name'].lower()
                        if test_context == run_config:
                            test.run_id = test_run['id']

        else:
            tests = [t.case_id for t in alltests._tests if t.case_id]
            logger.debug('Cases in current run: {}'.format(tests))
            run_id = config.api_client.create_test_run(tests)
            for test in alltests._tests:
                test.run_id = run_id
            logger.debug('Created test run {} using above cases'.format(
                          run_id))

    if not alltests.countTestCases():
        # FIXME: Really needed ? Can't we just rely on the number of tests run
        # ? -- vila 2013-06-04
        raise RuntimeError('Did not find any tests')

    if collect_only:
        for t in testtools.testsuite.iterate_tests(alltests):
            out.write(t.id() + '\n')
        return 0

    txt_res = results.TextTestResult(out, failfast=failfast, verbosity=2)
    if report_format == 'xml':
        results_file = os.path.join(results_directory, 'results.xml')
        xml_stream = open(results_file, 'w')
        result = testtools.testresult.MultiTestResult(
            txt_res, junitxml.JUnitXmlResult(xml_stream))
        result.failfast = failfast
    else:
        result = txt_res

    if concurrency_num == 1:
        suite = alltests
    else:
        suite = testtools.ConcurrentTestSuite(
            alltests, concurrency.fork_for_tests(concurrency_num))

    result.startTestRun()
    try:
        suite.run(result)
    except KeyboardInterrupt:
        out.write('Test run interrupted\n')
    result.stopTestRun()

    return len(result.failures) + len(result.errors)

def post_api_test_results():
    logger.debug("Sending test run results")
    try:
        config.api_client.send_results()
    except APIError as e:
        logger.debug("Could not send test results \n" + str(e))

def find_client_credentials(module):
    if module == 'sauce_config' and config.platform_config:
        mod_path = os.path.realpath(config.platform_config)
        module = os.path.basename(mod_path).strip('.py')
        return imp.load_source(module, mod_path)
    else:
        cwd = os.getcwd()
        mod_path = os.path.join(cwd, '{}.py'.format(module))
        if not os.path.isfile(mod_path):
            mod_path = os.path.join(os.path.dirname(cwd), '{}.py'.format(module))
        if not os.path.isfile(mod_path):
            mod_path = os.path.join(os.path.abspath(os.path.join(
                cwd, "../..")), '{}.py'.format(module))
        return imp.load_source(module, os.path.abspath(mod_path))

def set_client_credentials(client):
    if client == 'testrail':
        creds = find_client_credentials('testrail_config')
        config.api_client = testrail_helper.TestRailHelper(creds.url,
                                                           creds.user,
                                                           creds.password,
                                                           creds.project_id)
    elif client == 'saucelabs':
        return find_client_credentials('sauce_config')

    elif client == 'appium':
        return find_client_credentials('appium_config')

def find_shared_directory(test_dir, shared_directory):
    """This function is responsible for finding the shared directory.
    It implements the following rule:

    If a shared directory is explicitly specified then that is used.

    The test directory is checked first. If there is a shared directory
    there, then that is used.

    If the current directory is not "above" the test directory then the
    function bails.

    Otherwise it checks every directory from the test directory up to the
    current directory. If it finds one with a "shared" directory then it
    uses that as the shared directory and returns.

    The intention is that if you have 'tests/shared' and 'tests/foo' you
    run `sst-run -d tests/foo` and 'tests/shared' will still be used as
    the shared directory.

    IMHO the above is only needed because we don't allow:
    sst-run --start with tests.foo

    So I plan to remove the support for searching 'shared' upwards in favor of
    allowing running a test subset and go with a sane layout and import
    behavior. No test fail if this feature is removed so it's not supported
    anyway. -- vila 2013-04-26
    """
    if shared_directory is not None:
        return os.path.abspath(shared_directory)

    cwd = os.getcwd()
    default_shared = os.path.join(test_dir, 'shared')
    shared_directory = default_shared
    if not os.path.isdir(default_shared):
        relpath = os.path.relpath(test_dir, cwd)
        if not relpath.startswith('..') and not os.path.isabs(relpath):
            while relpath and relpath != os.curdir:
                this_shared = os.path.join(cwd, relpath, 'shared')
                if os.path.isdir(this_shared):
                    shared_directory = this_shared
                    break
                relpath = os.path.dirname(relpath)

    return os.path.abspath(shared_directory)
