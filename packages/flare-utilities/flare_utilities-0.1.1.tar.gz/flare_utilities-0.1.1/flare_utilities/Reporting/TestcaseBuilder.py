from dataclasses import dataclass, field
from typing import List

from flare_utilities.Reporting.HTMLBuilder import prepare_a_testcase


@dataclass
class TestcaseDetails():
    name: str = ''
    description: str = ''
    step_index: int = 1
    step_name: List[str] = field(default_factory=list)
    expected: List[str] = field(default_factory=list)
    actual: List[str] = field(default_factory=list)
    status: List[str] = field(default_factory=list)
    overall_status: str = 'green'
    exception_message: str = ''

    def add_step_name(self, element):
        self.step_name += element

    def add_expected(self, element):
        self.expected += element

    def add_actual(self, element):
        self.actual += element

    def add_status(self, element):
        self.status += element


def wrap_testcase(testcase_details):
    testcase_with_all_steps = consolidate_teststeps_for_testcase(
        testcase_details)
    return prepare_a_testcase(testcase_with_all_steps, testcase_details)


def consolidate_teststeps_for_testcase(testcase_details):

    listForReporting_step_names = testcase_details.step_name
    listForReporting_Expected = testcase_details.expected
    listForReporting_Actual = testcase_details.actual
    listForReporting_Status = testcase_details.status
    buildTestSteps_ExpectedActual = ""

    for i in range(len(listForReporting_Expected)):
        buildTestSteps_ExpectedActual = buildTestSteps_ExpectedActual + addRowForTestStep(
            (i+1),
            listForReporting_step_names[i],
            listForReporting_Expected[i],
            listForReporting_Actual[i],
            listForReporting_Status[i]
        )

    return buildTestSteps_ExpectedActual


def addRowForTestStep(colID, colName, expected, actual, testStepStatus):
    testStepicon = ""
    if testStepStatus == "PASS":
        testStepicon = '<i class="bi bi-check-circle"></i>'
    elif testStepStatus == "EXIT":
        testStepicon = '<i class="bi bi-bug-fill"></i>'
    else:
        testStepicon = '<i class="bi bi-x-circle"></i>'

    return f"""
        <tr>
          <td>{colID}</td>
          <td>{colName}</td>
          <td>{expected}</td>
          <td>{actual}</td>
          <td>{testStepicon}</td>
        </tr>
    """
