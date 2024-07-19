import json, requests, os
from ntpath import join
from .config import Config
from datetime import datetime

class Xray:
    def authentication() -> str:
        if os.getenv('JWT_TOKEN'):
            print("Autenticação via JWT TOKEN = ", os.getenv('JWT_TOKEN'))
            return 'Bearer ' + os.getenv('JWT_TOKEN')
        
        print("Token JWT não configurado, gerando outro...")
        XRAY_API = Config.xray_api()
        XRAY_CLIENT_ID = Config.xray_client_id()
        XRAY_CLIENT_SECRET = Config.xray_client_secret()

        json_data = json.dumps({'client_id': XRAY_CLIENT_ID, 'client_secret': XRAY_CLIENT_SECRET})
        resp = requests.post(f'{XRAY_API}/authenticate', data=json_data, headers={'Content-Type':'application/json'})
            
        if resp.status_code == 200:
            return 'Bearer ' + resp.json()
        else:
            print('Authentication error: ', resp.status_code)


    def createTestExecution():
        PROJECT_KEY = Config.project_key()
        XRAY_API = Config.xray_api()
        test_execution_date = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

        json_data = f'''
            mutation {{
                createTestExecution(
                    testIssueIds: [],
                    testEnvironments: [],
                    jira: {{
                        fields: {{
                            summary: "QA Automation Execution | { test_execution_date }",
                            project: {{ key: "{ PROJECT_KEY }" }}
                        }}
                    }}
                ) {{
                    testExecution {{
                        issueId
                        jira(fields: ["key"])
                    }}
                    warnings
                    createdTestEnvironments
                }}
            }}
        '''

        resp = requests.post(
            f'{XRAY_API}/graphql',
            json={ 'query': json_data },
            headers={
                'Content-Type': 'application/json',
                'Authorization': Xray.authentication()
            },
        )

        result = json.dumps({
            'issueId': resp.json().get('data').get('createTestExecution').get('testExecution').get('issueId'),
            'key': resp.json().get('data').get('createTestExecution').get('testExecution').get('jira').get('key')
        })

        if resp.status_code == 200:
            print('Created new test execution.')
            return json.loads(result)
        else:
            print('Error create test execution: ', resp.json())

    def importExecutionCucumber():
        PROJECT_KEY = Config.project_key()
        XRAY_API = Config.xray_api()

        print("cucumber.json file path:", join(Config.cucumber_path(), 'cucumber.json'))

        report = requests.post(f'{XRAY_API}/import/execution/cucumber', 
            data = open(Config.cucumber_path() + '/cucumber.json', 'rb'),
            params = { 
                'projectKey': PROJECT_KEY
            },
            headers = {
                'Content-Type': 'application/json',
                'Authorization': Xray.authentication()
            }
        )

        if report.status_code != 200:
            print('Error Cucumber import execution: ', report.status_code)
        else:
            print('Successfully sent Cucumber import execution.')
        
        print('Retorno: ', report.json())
