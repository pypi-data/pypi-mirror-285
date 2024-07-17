import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry


class RetrySession:
    def __init__(self, max_retry=5, backoff_factor=0.1, status_forcelist=(500, 502, 503, 504)):
        self.max_retry = max_retry
        self.backoff_factor = backoff_factor
        self.status_forcelist = status_forcelist
        self.session = requests.Session()

    def __enter__(self):
        retries = Retry(total=self.max_retry, backoff_factor=self.backoff_factor, status_forcelist=self.status_forcelist)
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()
