import logging
from dataclasses import dataclass, field
from typing import List

from flare_utilities.Reporting import FlareHTMLReporter, TestcaseBuilder

testcase_info = dict()

teststep_info = dict()
teststeps = dict()

scenario_index = 0
step_index = 0
log_index = 0

log_items_for_step = dict()
teststep_log_items = dict()

skip_following_steps_on_exception = 'false'


@dataclass
class STATUS:
    PASS: str = 'PASS'
    FAIL: str = 'FAIL'


def update_testlog(expected, actual, status: str):
    global log_index
    log_index += 1

    # Get step index
    teststep_log_items[log_index] = [expected, actual, status]

    if status.upper() == 'PASS':
        logging.info(actual)
    elif status.upper() == 'FAIL':
        logging.error(actual)


def catch_step_level_exception(context, exception_name):

    # Get step index
    global log_index
    log_index += 1

    exp_nm = f"ERROR: {repr(exception_name)}"

    # Get step index
    teststep_log_items[log_index] = ['-', exp_nm, 'EXIT']

    logging.critical(exp_nm)
    # sys.exit(exception_name)
    global skip_following_steps_on_exception
    skip_following_steps_on_exception = 'true'


def get_testcase_info(scenario_name):
    # Get test case ID and Scenario name
    global scenario_index
    scenario_index += 1

    testcase_info[scenario_index] = [
        f'Test case #{scenario_index}', scenario_name]

    teststeps.clear()


def get_teststep_info(step_name):
    global step_index
    step_index += 1

    teststeps[step_index] = [step_name]
    teststep_info[scenario_index] = teststeps.copy()


def save_teststep_logs():
    log_items_for_step[step_index] = teststep_log_items.copy()

    teststep_log_items.clear()


def final_testcase_collection_for_reporting():
    tmpTCCollection = list()

    for tc_num in testcase_info.keys():
        testcase_name = testcase_info.get(tc_num)[0]
        testcase_description = testcase_info.get(tc_num)[1]

        tc_detail = TestcaseBuilder.TestcaseDetails()

        for ts_num in teststep_info.get(tc_num):
            teststep_index = ts_num
            teststep_description = teststep_info.get(tc_num).get(ts_num)[0]

            logs = log_items_for_step.get(teststep_index)

            for log_index in logs.keys():

                tmparray = list()
                tmparray.append(teststep_description)

                for log in logs.get(log_index):

                    tmparray.append(log)

                tc_detail.name = testcase_name
                tc_detail.description = testcase_description
                tc_detail.add_step_name([tmparray[0]])
                tc_detail.add_expected([tmparray[1]])
                tc_detail.add_actual([tmparray[2]])
                tc_detail.add_status([tmparray[3]])

        tmpTCCollection.append(TestcaseBuilder.wrap_testcase(tc_detail))
    FlareHTMLReporter.start(tmpTCCollection)
    FlareHTMLReporter.showInBrowser()
