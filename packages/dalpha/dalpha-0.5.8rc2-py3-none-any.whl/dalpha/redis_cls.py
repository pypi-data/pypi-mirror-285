import json

from dalpha.logging import logger

class DalphaRedis:
    def __init__(self, client: str, db_num: int):
        self.rd = self.setup(db_num)
        self.client = client

    def setup(self, db_num):
        try:
            import redis
            from redis.backoff import ExponentialBackoff
            from redis.retry import Retry
            from redis.exceptions import (
            BusyLoadingError,
            ConnectionError,
            TimeoutError
            )
            retry = Retry(ExponentialBackoff(), 3)

        except ImportError:
            raise ImportError("Please install redis-py package -> pip install redis")
        
        return redis.StrictRedis(
            host="k8s-redis-redis-8a93856597-98eab959ed2cbb3e.elb.ap-northeast-2.amazonaws.com",
            port=6379,
            decode_responses=True,
            password=os.environ.get("REDIS_PASSWORD"),
            retry = retry,
            retry_on_error = [BusyLoadingError, ConnectionError, TimeoutError],
            db = db_num
        )

    def get(self, key: str):
        key = f"{self.client}-{key}"
        json_dict = self.rd.get(key)
        if json_dict:

            return_lst = json.loads(json_dict)
            return return_lst
        else:
            return None

    def set(self, key: str, value, expire: int = None):
        key = f"{self.client}-{key}"
        try:
            json_dict = json.dumps(value, ensure_ascii=False).encode("utf-8")
            self.rd.set(key, json_dict, ex=expire)
            return True
        except Exception as e:
            logger.error(f"Error : {e}")
            return False

    def delete(self, key: str):
        key = f"{self.client}-{key}"
        try:
            self.rd.delete(key)
            return True
        except Exception as e:
            logger.error(f"Error : {e}")
            return False
