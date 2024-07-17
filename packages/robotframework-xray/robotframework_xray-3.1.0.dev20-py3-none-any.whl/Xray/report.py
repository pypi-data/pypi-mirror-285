import platform, json
from ntpath import join
from .config import Config
import xml.etree.ElementTree as ET

class Report:
    def robot(report_json):
        report = ET.Element('robot', {
            'os': platform.system(),
            'python': platform.python_version(),
            'rpa': 'false',
            'schemaversion': '4',
        })

        for suite in report_json:
            sub_element_suite = ET.SubElement(report, 'suite', {
                'id': suite.get('id'),
                'name': suite.get('longname'),
                'source': suite.get('source'),
            })

            for test in suite.get('tests'):
                sub_element_test = ET.SubElement(sub_element_suite, 'test', {
                    'id': test.get('id'),
                    'name': test.get('originalname'),
                    'line': str(test.get('lineno')),
                })

                if test.get('tags'):
                    sub_element_tag = ET.SubElement(sub_element_test, 'tags')
                    for tag in test.get('tags'):
                        ET.SubElement(sub_element_tag, 'tag').text = tag

                for keyword in test.get('keywords'):
                    sub_element_keyword = ET.SubElement(sub_element_test, 'kw', {
                        'type': keyword.get('type'),
                        'name': keyword.get('kwname'),
                        'library': keyword.get('libname'),
                    })
                    
                    if keyword.get('args'):
                        sub_element_arguments = ET.SubElement(sub_element_keyword, 'arguments')
                        for arg in keyword.get('args'):
                            ET.SubElement(sub_element_arguments, 'arg').text = arg
                    
                    if keyword.get('doc'):
                        ET.SubElement(sub_element_keyword, 'doc').text = keyword.get('doc')

                    if keyword.get('messages'):
                        for message in keyword.get('messages'):
                            ET.SubElement(sub_element_keyword, 'msg', {
                                'timestamp': message.get('timestamp'),
                                'level': message.get('level'),
                                'html': message.get('html'),
                            }).text = message.get('message')
                    
                    if keyword.get('status'):
                        ET.SubElement(sub_element_keyword, 'status', {
                            'status': keyword.get('status'),
                            'starttime': keyword.get('starttime'),
                            'endtime': keyword.get('endtime'),
                        })

        ET.SubElement(report, 'doc').text = suite.get('doc')
        ET.SubElement(report, 'status', {
            'status': suite.get('status'),
            'starttime': suite.get('starttime'),
            'endtime': suite.get('endtime'),
        })

        xml = ET.ElementTree(report)
        xml.write(file_or_filename='report.xml', encoding='UTF-8', xml_declaration=True)


    def cucumber(report_json):
        cucumber = []
        for suite_index, suite in enumerate(report_json):
            cucumber.append({
                "keyword": "Feature",
                "name": suite.get('longname'),
                "line": 1,
                "description": suite.get('doc'),
                "tags": [],
                "id": suite.get('id'),
                "uri": suite.get('source'),
                "elements": [],
            })
            for test_index, test in enumerate(suite.get('tests')):
                cucumber[suite_index]['elements'].append({
                    "keyword": "Scenario",
                    "name": test.get('originalname'),
                    "line": test.get('lineno'),
                    "description": test.get('doc'),
                    "tags": [],
                    "id": test.get('id'),
                    "type": "scenario",
                    "steps": [],
                })
                for tag_index, tag in enumerate(test.get('tags')):
                    cucumber[suite_index]['elements'][test_index]['tags'].append({
                        "name": "@{}".format(tag),
                        "line": test.get('lineno'),
                    })
                for step_index, step in enumerate(test.get('keywords')):
                    if step.get('kwname').split()[0] in ['Given', 'When', 'Then', 'And', 'But', '*']:
                        cucumber[suite_index]['elements'][test_index]['steps'].append({
                            "embeddings": [],
                            "keyword": step.get('kwname').split()[0],
                            "name": step.get('kwname').replace(step.get('kwname').split()[0], '').strip(),
                            "line": step.get('lineno'),
                            "match": {
                                "arguments": [],
                                "location": "{}:{}".format(step.get('source'), step.get('lineno'))
                            },
                            "result": {
                                "status": ("passed" if step.get('status').lower() == "pass" else ("failed" if step.get('status').lower() == "fail" else "skipped")),
                                "duration": step.get('elapsedtime'),
                            }
                        })

        print('Cucumber data = ', cucumber)

        with open(Config.cucumber_path() + '/cucumber.json', 'w') as report_file:
            json.dump(cucumber, report_file, indent=4)