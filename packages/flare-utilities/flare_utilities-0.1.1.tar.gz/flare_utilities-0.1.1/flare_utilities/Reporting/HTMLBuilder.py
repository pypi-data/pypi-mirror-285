

class Header:
    @staticmethod
    def set_column_names() -> str:
        return f"""
            <tr>
                <th id="t-col-w-1">Test Step #</th>
                <th id="t-col-w-2">Test Step Description</th>
                <th id="t-col-w-2">Expected</th>
                <th id="t-col-w-2">Actual</th>
                <th id="t-col-w-1">Status</th>
            </tr>
        """

    @staticmethod
    def set_testcase_name_and_status(testcase_details) -> str:
        if "FAIL" in testcase_details.status or "EXIT" in testcase_details.status:
            testcase_details.overall_status = 'red'
        else:
            testcase_details.overall_status = 'green'
        return f"""
            <button class="accordion">
                <span id="testcase" style="color: {testcase_details.overall_status}">{testcase_details.name}</span>
            </button>
        """

    @staticmethod
    def set_testcase_description(description) -> str:
        return f"""
            <div class="testSummary">
                <p>{description}</p>
            </div>
        """

def prepare_a_testcase(testcase_with_all_steps, testcase_details):
    return f"""
        {Header.set_testcase_name_and_status(testcase_details)}
        <div class="panel">
            {Header.set_testcase_description(testcase_details.description)}  
            <table>
            {Header.set_column_names()}
            {testcase_with_all_steps}
            </table>
        
            <div class="exception" style="display:{'flex' if 'EXIT' in testcase_details.status else 'none'}">{testcase_details.actual[len(testcase_details.actual)-1]}</div>
        </div>
    """

class Body:
    @staticmethod
    def set_teststep_attachment_icon(colID):
        return f"""
        <a
            href="#"
            data-toggle="modal"
            data-target="#myModal{colID}"
            ><i class="bi bi-filetype-png"></i
        ></a>
        """

    @staticmethod
    def set_modal_header():
        return """
        <div class="modal-header">
            <button
                type="button"
                class="close"
                data-dismiss="modal"
                aria-label="Close"
            >
                <span aria-hidden="true">x</span>
            </button>
        </div>
        """

    @staticmethod
    def set_modal_footer():
        return """
        <div class="modal-footer">
            <button
                type="button"
                class="btn btn-danger"
                data-dismiss="modal"
            >
            Close
            </button>
        </div>
        """

    @staticmethod
    def set_testcase_attachment_screenshot(attachment):
        return f"""
        <div class="modal-body">
            <img src="{attachment}" alt="" />
        </div>
        """

    @staticmethod
    def set_teststep_attachment_modal(colID, attachment):
        return f"""
        <div class="modal fade" id="myModal{colID}" role="dialog">
            <div class="modal-dialog modal-dialog-centered" role="document">
                <div class="modal-content">
                    {Body.set_modal_header()}
                    {Body.set_modal_footer()}
                </div>
            </div>
        </div>
        """

def prepare_teststep_attachment(colID, attachment):
    return f"""
        {Body.set_teststep_attachment_icon(colID)}
        {Body.set_teststep_attachment_modal(colID, attachment)}
    """