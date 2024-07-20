import os, base64, pyscreenrec
# import attributes, config, report, xray
from .attributes import *
from .config import Config
from .report import Report
from .xray import Xray
from ntpath import join
from bs4 import BeautifulSoup
from robot.libraries.BuiltIn import BuiltIn

b = BuiltIn()

class Listener:
    """Optional base class for listeners using the listener API version 2."""
    ROBOT_LISTENER_API_VERSION = 2
    ROBOT_LIBRARY_SCOPE = "GLOBAL"

    def __init__(self):
        self.ROBOT_LIBRARY_LISTENER = self
        self.report = []
        self.suite_index = 0
        self.test_index = 0
        self.keyword_index = 0
        self.recorder = pyscreenrec.ScreenRecorder()

    def start_suite(self, name: str, attributes: StartSuiteAttributes):
        """Called when a suite starts."""
        self.report.append({
            "id": attributes.get('id'),
            "longname": attributes.get('longname'),
            "doc": attributes.get('doc') + ' Test Suite.',
            "metadata": attributes.get('metadata'),
            "source": attributes.get('source'),
            "suites": attributes.get('suites'),
            "tests": [],
            "totaltests": attributes.get('totaltests'),
            "starttime": attributes.get('starttime'),
        })

    def end_suite(self, name: str, attributes: EndSuiteAttributes):
        """Called when a suite end."""
        suite = self.report[self.suite_index]
        suite['endtime'] = attributes.get('endtime')
        suite['elapsedtime'] = attributes.get('elapsedtime')
        suite['status'] = attributes.get('status')
        suite['statistics'] = attributes.get('statistics')
        suite['message'] = attributes.get('message')

        self.suite_index += 1
        self.test_index = 0
        self.keyword_index = 0

    def start_test(self, name: str, attributes: StartTestAttributes):
        """Called when a test or task starts."""
        self.report[self.suite_index]['tests'].append({
            "id": attributes.get('id'),
            "longname": attributes.get('longname'),
            "originalname": attributes.get('originalname'),
            "doc": attributes.get('doc'),
            "tags": attributes.get('tags'),
            "template": attributes.get('template'),
            "source": attributes.get('source'),
            "lineno": attributes.get('lineno'),
            "starttime": attributes.get('starttime'),
            "endtime": '',
            "elapsedtime": 0,
            "message": '',
            "xraytest": '',
            "issueId": '',
            "keywords": [],
            "video": '',
        })

        selectedTag = ''
        for tag in attributes.get('tags'):
            if Config.project_key() in tag:
                test = self.report[self.suite_index]['tests'][self.test_index]
                test['xraytest'] = tag
                selectedTag = tag
        
        test['issueId'] = Xray.getTest(selectedTag)

        self.recorder.start_recording("{}.mp4".format(attributes.get('id')), 10)

    def end_test(self, name: str, attributes: EndTestAttributes):
        """Called when a test or task ends."""
        test = self.report[self.suite_index]['tests'][self.test_index]
        test['endtime'] = attributes.get('endtime')
        test['elapsedtime'] = attributes.get('elapsedtime')
        test['status'] = attributes.get('status')
        test['message'] = attributes.get('message')

        self.recorder.stop_recording()

        recording = "{}.mp4".format(attributes.get('id'))
        with open(recording, 'rb') as video_file:
            test['video'] = base64.b64encode(video_file.read()).decode('utf-8')

        if os.path.isfile(recording):
            os.remove(recording)
        
        self.test_index += 1
        self.keyword_index = 0

    def start_keyword(self, name: str, attributes: StartKeywordAttributes):
        """Called when a keyword or a control structure like IF starts.

        The type of the started item is in ``attributes['type']``. Control
        structures can contain extra attributes that are only relevant to them.
        """
        keyword = self.report[self.suite_index]['tests'][self.test_index]
        keyword['keywords'].append({
            "type": attributes.get('type'),
            "kwname": attributes.get('kwname'),
            "libname": attributes.get('libname'),
            "doc": attributes.get('doc'),
            "args": attributes.get('args'),
            "assign": attributes.get('assign'),
            "tags": attributes.get('tags'),
            "source": attributes.get('source'),
            "lineno": attributes.get('lineno'),
            "status": attributes.get('status'),
            "starttime": attributes.get('starttime'),
            "endtime": '',
            "elapsedtime": 0,
            "evidence": '',
        })

    def end_keyword(self, name: str, attributes: EndKeywordAttributes):
        """Called when a keyword or a control structure like IF ends.

        The type of the started item is in ``attributes['type']``. Control
        structures can contain extra attributes that are only relevant to them.
        """
        keyword = self.report[self.suite_index]['tests'][self.test_index]['keywords'][self.keyword_index]
        keyword['endtime'] = attributes.get('endtime')
        keyword['elapsedtime'] = attributes.get('elapsedtime')
        keyword['status'] = attributes.get('status')

        self.keyword_index = self.keyword_index + 1

    def log_message(self, message: MessageAttributes):
        """Called when a normal log message are emitted.

        The messages are typically logged by keywords, but also the framework
        itself logs some messages. These messages end up to output.xml and
        log.html.
        """
        if message['message'].__contains__('<img'):
            soup = BeautifulSoup(message['message'], 'html.parser')
            image_src = soup.img.get('src')

            if not image_src.__contains__('data:image/png;base64,'):
                with open(join(BuiltIn().get_variable_value('${OUTPUT_DIR}'), image_src), 'rb') as img_file:
                    b64_string = base64.b64encode(img_file.read())
                    keyword = self.report[self.suite_index]['tests'][self.test_index]['keywords'][self.keyword_index]
                    keyword['evidence'] = '{}'.format(b64_string.decode('utf-8'))
            else:
                keyword = self.report[self.suite_index]['tests'][self.test_index]['keywords'][self.keyword_index]
                keyword['evidence'] = image_src.replace('data:image/png;base64,', '')

    def message(self, message: MessageAttributes):
        """Called when framework's internal messages are emitted.

        Only logged by the framework itself. These messages end up to the syslog
        if it is enabled.
        """

    def library_import(self, name: str, attributes: LibraryAttributes):
        """Called after a library has been imported."""

    def resource_import(self, name: str, attributes: ResourceAttributes):
        """Called after a resource file has been imported."""

    def variables_import(self, name: str, attributes: VariablesAttributes):
        """Called after a variable file has been imported."""

    def output_file(self, path: str):
        """Called after the output file has been created.

        At this point the file is guaranteed to be closed.
        """

    def log_file(self, path: str):
        """Called after the log file has been created."""

    def report_file(self, path: str):
        """Called after the report file has been created."""

    def xunit_file(self, path: str):
        """Called after the xunit compatible output file has been created."""

    def debug_file(self, path: str):
        """Called after the debug file has been created."""

    def close(self):
        """Called when the whole execution ends.

        With library listeners called when the library goes out of scope.
        """
        Report.cucumber(self.report)
        testExecutionId = Xray.importExecutionCucumber()
        self._send_evidence(self.report, testExecutionId['id'])

    def _send_evidence(self, report, testExecutionId):        
        for suite in report:
            for test in suite['tests']:
                id = Xray.getTestRun(test['issueId'], testExecutionId)
                Xray.addEvidenceToTestRun(id, 'Evidence_{}.mp4'.format(test['xraytest']), "video/mp4", test['video'])
                print('- {}, evidence submitted successfully!'.format(test['originalname']))