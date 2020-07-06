from __future__ import absolute_import
from builtins import str
from builtins import range
import json
import logging
from datetime import datetime
from pytz import timezone
from sst import config
from .testrail_api import *

logger = logging.getLogger('SST')

class TestRailHelper:

    def __init__(self, url, user, password, project_id):
        self.client = APIClient(url)
        self.client.user = user
        self.client.password = password
        self.project_id = project_id
        self.run_results = {}
        self.runs = []
        self.plan_id = None

    def _get_time(self):
        return datetime.now(timezone('US/Eastern')).time().strftime('%I:%M %p')

    def _get_suite(self):
        return self.client.send_get('get_suites/{}'.format(self.project_id))

    def get_plan(self, plan_id):
        return self.client.send_get('get_plan/{}'.format(plan_id))

    def get_runs_in_plan(self, plan_id):
        plan = self.get_plan(plan_id)
        try:
            runs_list = []
            for entry in plan['entries']:
                for run in entry['runs']:
                    runs_list.append(run)
            return runs_list
        except Exception as e:
            logger.debug("Could not find test runs \n" + str(e))

    def create_test_plan(self):
        time = self._get_time()
        try:
            plan = self.client.send_post('add_plan/{}'.format(self.project_id),
                {
                    "name": "Automation Test Plan - {}".format(time)
                }
            )
            self.plan_id = plan['id']
            return plan
        except Exception as e:
            logger.debug("Could not create TestRail test plan \n" + str(e))

    def create_test_run(self, case_ids, platform=None):
        endpoint = None
        time = self._get_time()
        payload = {"include_all": False,
                   "case_ids": case_ids}

        if not platform:
            endpoint = 'add_run/{}'.format(self.project_id)
            payload.update({"name": "Automation Test Run {}".format(time)})
            try:
                run_id = self.client.send_post(endpoint, payload)['id']
                self.runs.append(run_id)
                return run_id
            except Exception as e:
                logger.debug("Could not create TestRail test run \n" + str(e))
        else:
            suite_id = self._get_suite()[0]['id']
            endpoint = 'add_plan_entry/{}'.format(self.plan_id)
            payload.update({"name": "Automation Test Run - {} - {}".format(
                                                                    platform,
                                                                    time),
                            "suite_id": suite_id
                            })
            try:
                run = self.client.send_post(endpoint, payload)
                run_data = dict(run_id=run['runs'][0]['id'], platform=platform)
                self.runs.append(run_data)
                return run_data
            except Exception as e:
                logger.debug("Could not create TestRail test run \n" + str(e))

    def _get_entry_id(self, run_id):
        endpoint = 'get_run/{}'.format(run_id)
        run = self.client.send_get(endpoint)

    def update_test_run(self, plan_id, entry_id, field, value):
        endpoint = 'update_plan_entry/{}/{}'.format(plan_id, entry_id)
        payload = {''.format(field) : ''.format(value)}
        try:
            self.client.send_post(endpoint, payload)
        except Exception as e:
            logger.debug("Could not update TestRail test run \n" + str(e))

    # add test case results to test run
    def send_results(self):
        self.store_json_results(self.run_results)
        try:
            for r in self.runs:
                run = self.client.send_post('add_results_for_cases/{}'
                                            .format(r['run_id']),
                                            {'results': self.run_results}
                                            )
        except Exception as e:
            logger.debug("Could not send TestRail results \n" + str(e))

    # add individual test case result to test run
    def send_result(self, run_id, case_id, status_id, comment=None):
        result = {
            "status_id": status_id,
            "comment": comment
        }
        self.store_json_results(result, case_id)
        if not run_id:
            logger.debug("Run ID does not exist")
            return None
        try:
            run = self.client.send_post('add_result_for_case/{}/{}'
                                        .format(run_id, case_id), result)
        except Exception as e:
            logger.debug("Could not send TestRail results \n" + str(e))

    def store_json_results(self, result, case_id=''):
        filename = '{}/{}results.json'.format(config.results_directory, case_id)
        with open(filename, 'w') as outfile:
            json.dump(result, outfile)


class APITestStatus:

    PASSED, BLOCKED, RETEST, RETEST, FAILED = list(range(1, 6))


FAILED_TEST_RESULT_STATUS = APITestStatus.FAILED
