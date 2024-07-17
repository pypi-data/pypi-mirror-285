import json
import os
import time
from typing import Optional
import requests
import sentry_sdk

from dalpha.request import RetrySession
from dalpha.logging import logger

def internal_call(
        service_code: str,
        metadata: dict,
        dev_server = bool(os.environ.get('DEV_SERVER', 'True') == 'True'),
        key: str = os.environ.get('INTERNAL_KEY'),
        x_api_key: str = os.environ.get('INTERNAL_X_API_KEY'),
        polling_interval: float = 0.5,
        time_out: float = 60
    ):
    '''
    service_code : 서비스 코드
    key : key
    metadata : 요청할 메타데이터
    polling_interval : 폴링 간격
    max_polling_time : 최대 폴링 횟수
    time_out : 최대 폴링 시간 (초), 폴링을 시작한 후 time_out 초가 지나면 폴링을 중단하고 exception 발생
    '''
    if polling_interval < 0.1:
        raise ValueError("Polling interval should not be less than 0.1")
    header = {
        'X-Api-Key': x_api_key,
        'Content-Type': 'application/json'
    }
    base_url = os.environ.get('DEV_BASE_URL', 'https://api.exp.dalpha.so') if dev_server else os.environ.get('BASE_URL', 'https://api.dalpha.so')
        
    url = os.path.join(base_url, f'partner/polling/{service_code}/{key}')
    with RetrySession() as s:
        response = s.post(url, headers=header, data=json.dumps(metadata))
        if response.status_code == 200:
            eval_id = response.json()['id']
        else:
            message = f'error from internal_call(post) / response status_code {response.status_code}: {response.text}'
            sentry_sdk.capture_message(message)
            raise Exception(message)
    while time_out > 0:
        time.sleep(polling_interval)
        time_out -= polling_interval
        with RetrySession() as s:
            response = s.get(os.path.join(base_url, f'partner/{service_code}/{key}/{eval_id}'), headers=header)
            if response.status_code == 202:
                continue
            elif response.status_code == 200:
                if response.json()['success'] == True:
                    return response.json()['payload']
                else:
                    message = f'error response from internal_call(get) / response status_code {response.status_code}: {response.text}'
                    sentry_sdk.capture_message(message)
                    raise Exception(message)
            else:
                message = f'error from internal_call(get) / response status_code {response.status_code}: {response.text}'
                sentry_sdk.capture_message(message)
                raise Exception(message)
    message = f'internal call result is not returned in timeout({time_out}) seconds.'
    sentry_sdk.capture_message(message)
    raise Exception(message)

def slack_alert(channel_name, text, token, dev_server = bool(os.environ.get('DEV_SERVER', 'True') == 'True')):
    base_url = os.environ.get('DEV_BASE_URL', 'https://api.exp.dalpha.so') if dev_server else os.environ.get('BASE_URL', 'https://api.dalpha.so')
    url = os.path.join(base_url, f'slack/message')
    header = {
        'token': token,
        'Content-Type': 'application/json'
    }
    payload = {
        "channelName": channel_name,
        "message": text
    }
    with RetrySession() as s:
        response = s.post(url, headers=header, data=json.dumps(payload))
    if response.status_code == 200:
        return response.text
    elif response.status_code < 500: # 400대 에러일 때는 확실히 유효하지 않은 메세지로 판단
        logger.warning(f'error from slack_alert / response status_code {response.status_code}: {response.text}')
        return None
    else: # 5회 재시도해도 500대 에러일 때는 유효한지 알 수 없으므로 유효하지 않은 메세지로 판단
        logger.error(f'error from slack_alert / response status_code {response.status_code}: {response.text}')
        return None

class BackendCli:
    def __init__(self, api_id, dev_server, token):
        self.api_id = api_id
        self.dev_server = dev_server
        self.base_url = os.environ.get('DEV_BASE_URL', 'https://api.exp.dalpha.so') if dev_server else os.environ.get('BASE_URL', 'https://api.dalpha.so')
        self.token = token
        self.header = {
            'token': self.token,
            'Content-Type': 'application/json'
        }
        
    def get_internal_slack(self):
        try:
            url = os.path.join(self.base_url, f'inferences/{self.api_id}/owner')
            response = requests.request("GET", url, headers=self.header)
            account_id = response.json()
            if account_id == -1:
                return "<!subteam^S05EP7HQ18V>"
            url = os.path.join(self.base_url, f'accounts/{account_id}/internal_slack')
            response = requests.request("GET", url, headers=self.header)
            return '<@'+ response.text + '>'
        except Exception as e:
            return 'error'
        
    def get_inference(self):
        url = os.path.join(self.base_url, f'inferences/{self.api_id}')
        response = requests.request("GET", url, headers=self.header)

        return response
    
    def get_evaluate(self, evaluate_id: int):
        url = os.path.join(self.base_url, f'inferences/{self.api_id}/evaluate/id-poll/{evaluate_id}')
        with RetrySession() as s:
            response = s.get(url, headers=self.header)
        if response.status_code == 200:
            return response.json()
        elif response.status_code < 500: # 400대 에러일 때는 확실히 유효하지 않은 메세지로 판단
            logger.warning(f'error from check message validation / response status_code {response.status_code}: {response.text} \n poll function will return None.')
            return None
        else: # 5회 재시도해도 500대 에러일 때는 유효한지 알 수 없으므로 유효하지 않은 메세지로 판단
            logger.error(f'error from check message validation / response status_code {response.status_code}: {response.text} \n poll function will return None.')
            return None
        
    def poll(self):
        url = os.path.join(self.base_url, f'inferences/{self.api_id}/evaluate/poll')
        with RetrySession() as s:
            try:
                response = s.get(url, headers=self.header, timeout=10)
            except requests.exceptions.Timeout:
                logger.warning(f'error from poll / time-out \n poll function will return None.')
                return None
        if response.status_code == 422:
            return None
        elif response.status_code != 200:
            logger.warning(f'error from poll / response status_code {response.status_code}: {response.text} \n poll function will return None.')
            return None
        return response.json()
    
    def validate(self, evaluate_id: int, output: dict, usage: int = 1):
        with RetrySession() as s:
            url = os.path.join(self.base_url, f'inferences/{self.api_id}/evaluate/validate')
            payload = json.dumps({
                "id": evaluate_id,
                "json": output
            })
            response = s.put(url, headers=self.header, data=payload, params={'usage': usage})
            if response.status_code == 200:
                return
            else:
                message = f'error from validate / response status_code {response.status_code}: {response.text}'
                sentry_sdk.capture_message(message)
                raise Exception(message)
            
    def validate_error(self, evaluate_id: int, output: dict):
        with RetrySession() as s:
            url = os.path.join(self.base_url, f'inferences/{self.api_id}/evaluate/error')
            payload = json.dumps({
                "id": evaluate_id,
                "error": output
            })
            response = s.put(url, headers=self.header, data=payload)
            if response.status_code == 200:
                return
            else:
                message = f'error from validate_error / response status_code {response.status_code}: {response.text}'
                sentry_sdk.capture_message(message)
                raise Exception(message)

    def stream_validate(self, evaluate_id: int, output: dict):
        with RetrySession() as s:
            url = os.path.join(self.base_url, f'inferences/{self.api_id}/evaluate/stream/validate')
            payload = json.dumps({
                "id": evaluate_id,
                "json": output
            })
            response = s.put(url, headers=self.header, data=payload)
            if response.status_code == 200:
                return response.json()
            else:
                message = f'error from validate_stream / response status_code {response.status_code}: {response.text}'
                sentry_sdk.capture_message(message)
                raise Exception(message)
