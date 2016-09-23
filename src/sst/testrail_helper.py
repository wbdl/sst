import json
import logging
from datetime import datetime
from pytz import timezone
from sst import config
from testrail_api.testrail import *

logger = logging.getLogger('SST')

class TestRailHelper(object):

    def __init__(self, url, user, password, project_id):
        self.client = APIClient(url)
        self.client.user = user
        self.client.password = password
        self.project_id = project_id
        self.run_results = []
        self.run_id = None

    def create_test_run(self, case_ids):
        tz = timezone('US/Eastern')
        time = datetime.now(tz).time().strftime("%I:%M %p")
        try:
            run = self.client.send_post('add_run/{}'.format(self.project_id),
                  {
                      "name": "Automation Test Run {}".format(time),
                      "include_all": False,
                      "case_ids": case_ids
                  }
            )
            return run['id']
        except Exception as e:
            logger.debug("Could not create TestRail test run \n" + str(e))

    # add test case results to test run
    def send_results(self):
        self.store_json_results(self.run_results)
        try:
            run = self.client.send_post('add_results_for_cases/{}'
                      .format(self.run_id),
                      { "results": self.run_results }
            )
        except Exception as e:
            logger.debug("Could not send TestRail results \n" + str(e))

    # add individual test case result to test run
    def send_result(self, case_id, status_id, comment=None):
        result = {
            "status_id": status_id,
            "comment": comment
        }
        self.store_json_results(result, case_id)
        try:
            run = self.client.send_post('add_result_for_case/{}/{}'
                                        .format(self.run_id, case_id), result)
        except Exception as e:
            logger.debug("Could not send TestRail results \n" + str(e))

    def store_json_results(self, result, case_id=''):
        filename = '{}/{}results.json'.format(config.results_directory, case_id)
        with open(filename, 'w') as outfile:
            json.dump(result, outfile)


class APITestStatus(object):

    PASSED, BLOCKED, RETEST, RETEST, FAILED = range(1, 6)


FAILED_TEST_RESULT_STATUS = APITestStatus.FAILED
