import logging
import json, requests
import os
from ntpath import join
from datetime import datetime
from .config import Config
from .utils import find_tag

logger = logging.getLogger(__name__)

class Xray:
    '''
    Classe responsável pela comunicação com a API do X-Ray.
    Documentação oficial: https://docs.getxray.app/display/XRAY/v2.0.
    '''

    XRAY_API : str = Config.xray_api()
    PROJECT_KEY : str = Config.project_key()
    

    def authentication(self) -> str:
        '''
        Realiza a autenticação na API e retorna o token que deve 
        ser utilizado nas outras requisições.
        '''
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


    def createTestExecution(self, test_plan_key : str, tests):
        test_execution_date = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

        suite_data = {
            "summary": "Execução automática do Robot",
            "startDate": test_execution_date,
            "testPlanKey": test_plan_key
        }
        test_data = []
        for test in tests:
            print(test.tags)
            test_data.append({
                "testKey": find_tag(test.tags),
                "start": test_execution_date,
                "status": "EXECUTING"
            })

        print(suite_data)
        print(test_data)
        
        response = requests.post(
            f'{self.XRAY_API}/import/execution',
            json={ 'info': suite_data, 'tests': test_data },
            headers={
                'Content-Type': 'application/json',
                'Authorization': self.authentication()
            },
        )

        if response.status_code == 200:
            result = json.dumps({
                'issueId': response.json().get('data').get('createTestExecution').get('testExecution').get('issueId'),
                'key': response.json().get('data').get('createTestExecution').get('testExecution').get('jira').get('key')
            })
            print('Created new test execution: ', result['key'])
            return json.loads(result)
        else:
            logger.error('Error create test execution: ', response.json())
    
    
    def save_step(self):
        pass


    def save_screenshot(self):
        pass
