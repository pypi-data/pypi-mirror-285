import requests, sys, os, pkg_resources
from dalpha.logging import logger


def __load_config(file_path):
    if not os.path.isfile(file_path):
        logger.warning(f"{file_path} 파일을 찾을 수 없습니다.")
        return
    
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    for line in lines:
        line = line.strip()
        if line and not line.startswith("#"):
            key, value = line.split("=")
            if bool(os.environ.get("DEV_SERVER", 'True') == 'True') or os.environ.get(key) is None:
                os.environ[key] = value


def check_package_version(package_name):
    installed_version = pkg_resources.get_distribution(package_name).version
    try:
        url = f"https://pypi.org/pypi/{package_name}/json"
        response = requests.get(url)
        data = response.json()
        latest_version = data["info"]["version"]
        if latest_version != installed_version:
            logger.warning(" dalpha sdk 버전 -> " + installed_version + " / 최신 버전 -> " + latest_version)
        else:
            logger.info(" dalpha sdk 버전 -> " + installed_version + " (latest)")
    except Exception as e:
        logger.warning(f"dalpha sdk 버전 확인 중 오류가 발생했습니다:{e}")
cfg_path = os.path.join(sys.path[0],'.dalphacfg')


__load_config(cfg_path)
check_package_version("dalpha")

from dalpha.signal_handler import get_shutdown_requested
from dalpha.context import clear_context_evaluate, set_context, set_context_evaluate, get_context, Context
from dalpha.logging.events import Event

from dalpha.dto import InferenceResult, UpdateResult
from dalpha.exception import BaseStatusCode, ExpectedError, WaitException

from dalpha.agent import Agent
from dalpha.cobra_cls import Cobra
from dalpha.data_update_cls import DalphaDataUpdater
from dalpha.inference_cls import DalphaAI
from dalpha.redis_cls import DalphaRedis
from dalpha.openai_cls import DalphaOpenAI
from dalpha.backend_cli import BackendCli, internal_call, slack_alert
from dalpha.message_consumer import EvaluateItem
from dalpha.data_update_consumer import DataUpdateItem
import dalpha.s3 as s3
