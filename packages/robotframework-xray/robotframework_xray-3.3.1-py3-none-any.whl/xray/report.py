import json
# import config
from .config import Config

class Report:
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

                screenshots = []
                for step_index, step in enumerate(test.get('keywords')):
                    if step.get('evidence') != "":
                        screenshots.append({  "mime_type": "image/png",  "data": step.get('evidence') })
                    
                    if step.get('kwname').split()[0] in ['Given', 'When', 'Then', 'And', 'But', '*']:
                        cucumber[suite_index]['elements'][test_index]['steps'].append({
                            "embeddings": screenshots,
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
                        screenshots = []

        with open(Config.cucumber_path() + '/report.json', 'w') as report_file:
            json.dump(report_json, report_file, indent=4)

        with open(Config.cucumber_path() + '/cucumber.json', 'w') as report_file:
            json.dump(cucumber, report_file, indent=4)