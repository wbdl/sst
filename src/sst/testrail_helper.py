import json
import logging
from datetime import datetime
from testrail_api.testrail import *

logger = logging.getLogger('SST')

client = APIClient('https://dramafever.testrail.net/')

client.user = ''
client.password = ''

run_results = []
project_id = 3
run_id = None

FAILED_TEST_RESULT_STATUS = APITestStatus.FAILED

def create_test_run(case_ids):
    time = datetime.now().time().strftime("%I:%M %p")
    try:
        run = client.send_post('add_run/{}'.format(project_id),
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
def send_results():
    store_json_results(run_results)
    try:
        run = client.send_post('add_results_for_cases/{}'.format(run_id),
    		{ "results": run_results }
        )
    except Exception as e:
        logger.debug("Could not send TestRail results \n" + str(e))

# add individual test case result to test run
def send_result(case_id, status_id, comment=None):
    result = {
        "status_id": status_id,
        "comment": comment
    }
    store_json_results(result, case_id)
    try:
        run = client.send_post('add_result_for_case/{}/{}'
                               .format(run_id, case_id), result)
    except Exception as e:
        logger.debug("Could not send TestRail results \n" + str(e))

def store_json_results(result, case_id=None):
    path = '../' if not case_id else ''
    case_id = case_id or 'suite'
    with open('{}json_results_{}.txt'.format(path, case_id), 'w') as outfile:
        json.dump(result, outfile)


class APITestStatus(object):

    PASSED, BLOCKED, RETEST, RETEST, FAILED = range(1, 6)
