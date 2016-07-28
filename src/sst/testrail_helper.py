import json
import logging
from datetime import datetime
from testrail import *

logger = logging.getLogger('SST')

client = APIClient('https://dramafever.testrail.net/')

client.user = ''
client.password = ''

run_results = []
project_id = None
run_id = None

def create_test_run(case_ids):
    time = datetime.now().time().strftime("%I:%M %p")
    try:
        run = client.send_post('add_run/{}'.format(project_id),
            {
                "name": "Automation Test Run {}".format(time),
                "case_ids": case_ids
            }
        )
        return run['id']
    except Exception as e:
        logger.debug("Could not create TestRail test run \n" + str(e))

# add test case results to test run
def send_results():
    try:
        run = client.send_post('add_results_for_cases/{}'.format(run_id),
    		{ "results": run_results }
        )
    except Exception as e:
        logger.debug("Could not send TestRail results \n" + str(e))

# add individual test case result to test run
def send_result(case_id, status_id, comment=None):
    try:
        run = client.send_post('add_result_for_case/{}/{}'.format(run_id, case_id),
            {
            	"status_id": status_id,
            	"comment": comment
             }
        )
    except Exception as e:
        logger.debug("Could not send TestRail results \n" + str(e))


class APITestStatus(object):

    PASSED, BLOCKED, RETEST, RETEST, FAILED = range(1, 6)
