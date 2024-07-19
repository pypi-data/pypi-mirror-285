import os
import shutil
import webbrowser
from configparser import ConfigParser
from dataclasses import dataclass
from datetime import datetime


@dataclass
class FlareDefaults:
    current_directory: str = os.path.dirname(__file__)
    root_directory: str = os.path.abspath(os.curdir)
    reports_directory: str = f'{root_directory}/Reports/'

    testrun_folder_name: str = f'TestRun_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}'

    css_template_directory: str = f'{current_directory}/style.css'
    current_test_run_directory: str = f'{reports_directory}{testrun_folder_name}'
    html_template_directory: str = f'{current_directory}/index.html'
    flare_report_save_as: str = f'{current_test_run_directory}/Flare - Test Summary Report.html'


def start(tc_collection):

    # Copy CSS file to the recently created test run folder
    shutil.copy(FlareDefaults.css_template_directory,
                FlareDefaults.current_test_run_directory)

    html_template = open(FlareDefaults.html_template_directory, 'r')
    flare_report = open(FlareDefaults.flare_report_save_as, 'w')

    for line in html_template:
        if ('^^Testcases_Section^^' in line):

            for tc in tc_collection:
                flare_report.write(line.replace(line, tc))
        else:
            flare_report.write(line)

    html_template.close()
    flare_report.close()


def showInBrowser():
    config = ConfigParser()
    config.read(f'{FlareDefaults.root_directory}/behave.ini')
    reveal_report = config.get('flare', 'show_report_after_execution')
    if reveal_report.upper() == 'TRUE':
        webbrowser.open(FlareDefaults.flare_report_save_as)


def create_testrun_reports_directory():
    os.makedirs(FlareDefaults.current_test_run_directory)
