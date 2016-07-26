import json
import logging
from testrail import *

logger = logging.getLogger('SST')

client = APIClient('https://dramafever.testrail.net/')

client.user = ''
client.password = ''

run_results = []

# add test case results to test run
def send_results(run_id=88):
    try:
        run = client.send_post('add_results_for_cases/{}'.format(run_id),
    		{ "results": run_results }
        )
    except Exception as e:
        logger.debug("Could not send TestRail results \n" + str(e))

# add individual test case result to test run
def send_result(case_id, status_id, comment=None, run_id=88):
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
