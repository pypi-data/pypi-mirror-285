import inspect
from numbers import Number
import os
import re
import requests
import subprocess
import traceback
from typing import Any, Optional, Tuple
import multiprocessing
from time import sleep
from unittest import TestResult

SAPHIRA_URL = os.getenv('SAPHIRA_URL', 'https://prod.saphira.ai')
SAPHIRA_TOKEN = os.getenv('SAPHIRA_API_TOKEN')
HEADERS = {"Authorization": SAPHIRA_TOKEN}

# TODO: Integrate this into Matlab
# This registers as a daemon that will re-run the parent program
# TODO: Move daemon registration to service
def get_param(datasource: str, name: str, skip_threading: bool=False, local_runtime: bool=False) -> Any:
    # Get from service
    url = f'{SAPHIRA_URL}/get_single_data/' + name
    params = {
        'projectUuid': datasource,
    }
    consuming_application = inspect.stack()[-1].filename
    resp = requests.get(url, params, headers=HEADERS)
    print(f"{url} responded with status code {resp.status_code}")
    if resp.status_code != 200:
        print(f"Error fetching data: {resp.text}")
        return None

    print(f"Retrieved {resp.json()}")
    result = resp.json().get('latest_version', {}).get('value')

    if not skip_threading:
        if local_runtime:
            def loop():
                while True:
                    if get_param(datasource, name, skip_threading=True) != result:
                        subprocess.call(['python', consuming_application])
                    sleep(1)
            t = multiprocessing.Process(target=loop)
            t.start()
        else:
            # TODO: Perform proper dependency tracing to also upload any other linked files and build a Pipfile for execution
            upload_url = f'{SAPHIRA_URL}/upload?project={datasource}&requirement={name}'
            stack = inspect.stack()
            cwd = os.getcwd()
            files = {f'file{i}': open(stack[1 + i].filename, 'rb') for i in range(len(stack) - 1) if cwd in stack[1 + i].filename}
            upload_resp = requests.post(upload_url, files=files, headers=HEADERS)
            print(f"{upload_url} responded with status code {upload_resp.status_code}")
            if upload_resp.status_code != 200:
                print(f"Upload failed with {upload_resp.text}")

    return result

def update_test_status(project: str, requirement: str, passing: bool = False, test_result: Optional[TestResult] = None, exception: Exception = None, test: str = ''):
    stack = inspect.stack()
    if not test:
        test = stack[-1].filename.split('/')[-1]
    # Extract failure information from test_result (also include errors, not just failures)
    failure = ''
    if test_result:
        passing = test_result.wasSuccessful()
        if len(test_result.failures) > 0:
            # TODO: Add safety here
            failure = test_result.failures[0][1].split('\n')[-3].split('(')[1].split(" ")[0]
            # TODO: Traverse AST for source of this variable instead
            with open(test) as f:
                for line in f.readlines():
                    if re.match('.*' + failure + '.*=', line):
                        failure = line.split('=')[1]
                        break
            if '.' in failure:
                failure = failure.split('.')[0]
    elif exception:
        passing = False
        print(f"exception: {traceback.format_exc()}")
        failure = traceback.format_exc().split('\n')[-6].split('.')[0].split(" ")[-1]

    print(f"failure: {failure}")

    resp = requests.post(f'{SAPHIRA_URL}/update_test_status', json={'key': requirement, 
                                                                    'passing': passing, 
                                                                    'project': project, 
                                                                    'test': test,
                                                                    'failure': failure}, headers=HEADERS)
    print(resp.text)

def create_or_update(project: str, key: str, value: Any, unit: str, description: str, parents: str) -> str:
    resp = requests.post(f'{SAPHIRA_URL}/add_requirement?projectUuid={project}', 
                         json={'key': key, 
                               'requirement_type': 'numerical' if isinstance(value, Number) else 'text', 
                               'value': value,
                               'unit': unit,
                               'reason': description, 
                               'parents': parents}, headers=HEADERS)
    return resp

def save_manual_test_input(project: str, test_name: str, stdin_input_str: str) -> Tuple[str, str]:
    resp = requests.post(f'{SAPHIRA_URL}/save_manual_test_input', 
                         json={'project_id': project,
                               'title': test_name, 
                               'manual_test_inputs': stdin_input_str}, headers=HEADERS)
    print(resp.json())
    return resp.json().get('message').split('for requirement ')[1].split(' within project')[0], resp.json().get('s3_link')
