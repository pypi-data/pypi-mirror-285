import sys, os
import time
import sentry_sdk
from dataclasses import asdict
from typing import List

from dalpha.backend_cli import BackendCli
from dalpha.message_consumer import EvaluateItem, KafkaMessageConsumer, RawMessageConsumer, SqsMessageConsumer, to_evaluate_item
from dalpha.signal_handler import get_shutdown_requested
from dalpha.context import clear_context_evaluate, set_context, set_context_evaluate, get_context, Context
from dalpha.logging import logger
from dalpha.logging.events import Event

from dalpha.exception import BaseStatusCode


class Agent:
    # 1. constructor 로 넣어주는 경우
    # TODO(XXX): constructor 로 넣어주는 것은 production 코드에서는 지양해야 함.
    # ai-project-template 에서 production image build test code 에 넣어줄 것
    # 2. 환경변수로 넣어주는 경우
    # 3. .dalphacfg 로 넣어주는 경우

    # backend 에서 당겨오는 env
    # SQS 주소, Kafka 주소, service code 는 백엔드에서 받아옴
    # To-Be: 다른 AI 콜 해주는 Agent 의 token

    def __init__(
        self,
        api_id: int = int(os.environ.get('API_ID', 0)),
        use_sqs: bool = bool(os.environ.get('USE_SQS', 'False') == 'True'),
        use_kafka: bool = bool(os.environ.get('USE_KAFKA', 'False') == 'True'),
        dev_server: bool = bool(os.environ.get('DEV_SERVER', 'True') == 'True'),
    ):
        if not isinstance(api_id, int): raise TypeError('api_id is not a int')
        if not isinstance(use_sqs, bool): raise TypeError('use_sqs is not a bool')
        if not isinstance(dev_server, bool): raise TypeError('dev_server is not a bool')
        if not isinstance(use_kafka, bool): raise TypeError('use_kafka is not a bool')

        self.token = os.environ['TOKEN']
        self.sentry_dsn = os.environ['SENTRY_DSN']
        if dev_server:
            self.sentry_env = "exp"
        else:
            self.sentry_env = "production"

        self.backend_cli = BackendCli(
            api_id = api_id,
            dev_server = dev_server,
            token = self.token
        )

        inference = self.backend_cli.get_inference()
        if inference.status_code != 200:
            logger.warning(f'error from get sqs url / response status_code {inference.status_code}: {inference.text}')
            self.service_code = None
        else:
            self.queue_url = inference.json().get('sqs', None)
            self.kafka_topic = inference.json().get('kafkaTopic', None)
            self.service_code = inference.json().get('serviceCode', None)

        self.mock = {}

        '''
        if self.kafka_topic is not None:
        elif self.queue_url is not None:
        else:
        로 분기처리 할 것인지 고민해보기
        '''
        if use_kafka:  # 우선순위 1. kafka
            self.message_consumer = KafkaMessageConsumer(
                api_id = api_id,
                backend_cli = self.backend_cli,
                kafka_topic = self.kafka_topic
            )
        elif use_sqs:  # 우선순위 2. sqs (kafka가 없을 때만 사용)
            self.message_consumer = SqsMessageConsumer(
                api_id = api_id,
                backend_cli = self.backend_cli,
                queue_url=self.queue_url
            )
        else:
            self.message_consumer = RawMessageConsumer(
                api_id = api_id,
                backend_cli = self.backend_cli
            )

        self.poll_time = None

        set_context(Context(
            inference_id = api_id,
            service_code = self.service_code,
            env = "exp" if dev_server else "prod"
        ))
        sentry_sdk.set_context("context",asdict(get_context()))
        sentry_sdk.init(
            dsn=self.sentry_dsn,

            # Set traces_sample_rate to 1.0 to capture 100%
            # of transactions for performance monitoring.
            # We recommend adjusting this value in production.
            traces_sample_rate=1.0,
            environment = self.sentry_env
        )
        sentry_sdk.set_tag("api_id", api_id)
        sentry_sdk.set_tag("service_code", self.service_code)
        sentry_sdk.set_tag("engineer", self.backend_cli.get_internal_slack() )
        logger.info(
            message = "Dalpha agent initialized",
            event = Event.AGENT_INIT,
            data = {
                'inference_id': api_id,
                "dev_server": dev_server,
                "queue_url": self.queue_url,
                "sentry_dsn": self.sentry_dsn,
            }
        )

    def set_mock(self, mock):
        self.mock = mock
    
    def poll(self, max_number_of_messages = 1, mock=True):
        if get_shutdown_requested():
            logger.info(
                "System shutdown gracefully",
                event = Event.SHUTDOWN
            )
            self.message_consumer.close()
            sys.exit(0)
        if not isinstance(max_number_of_messages,int): TypeError("max_number_of_messages is not a int")
        if not isinstance(mock, bool): TypeError("mock is not a bool")
        if mock:
            logger.info(
                f"return mock: {to_evaluate_item(self.mock)}",
                data = to_evaluate_item(self.mock)
            )
            return to_evaluate_item(self.mock)

        ret: List[EvaluateItem] = self.message_consumer.poll()
        if len(ret) == 0:
            # 가져온 메세지가 없으면 None 반환
            return None
        elif len(ret) == 1:
            print(ret)
            # 가져온 메세지가 1개면 list 형태가 아닌 낱개로 반환
            logger.info(
                message = f"return evaluate item: {ret[0]}",
                event = Event.POLL,
                data = ret[0]
            )
            set_context_evaluate(
                evaluate_id=ret[0].id,
                account_id=ret[0].accountId
            )
            sentry_sdk.set_context("context",asdict(get_context()))
            self.poll_time = time.time()
            return ret[0]
        else:
            # 가져온 메세지가 여러개면 list 형태로 반환
            logger.info(
                message = f"return evaluate item: {ret}",
                event = Event.POLL,
                data = ret
            )
            self.poll_time = time.time()
            return ret
        
    def validate(self, evaluate_id, output, mock=True, log=True, inference_time=None, usage=1):
        try:
            if mock:
                logger.info(message = f"validate payload - {output}")
                return
            if inference_time == None and self.poll_time != None:
                inference_time = time.time() - self.poll_time
                self.poll_time = None
            self.message_consumer.commit(evaluate_id)
            if log:
                logger.info(
                    message = f"validate payload - {output}",
                    event = Event.VALIDATE,
                    properties = {
                        "evaluate_id": evaluate_id,
                        "inference_time": inference_time,
                    },
                    data = output
                )
            self.backend_cli.validate(evaluate_id, output, usage)
        finally:
            clear_context_evaluate()

    def validate_error(self, evaluate_id, output, mock=True, error_code=BaseStatusCode.INTERNAL_ERROR):
        try:
            if not isinstance(evaluate_id, int): raise TypeError('evaluate_id is not a int')
            if not isinstance(output, dict): raise TypeError('output is not a dict')
            if not isinstance(mock, bool): raise TypeError('mock is not a bool')
            output["code"] = error_code.value
            if mock:
                logger.info(message = f"validate_error payload - {output}")
                return

            self.message_consumer.commit(evaluate_id)

            logger.info(
                message = f"validate_error payload - {output}",
                event = Event.VALIDATE_ERROR,
                properties = {
                    "evaluate_id": evaluate_id,
                },
                data = output
            )
            self.backend_cli.validate_error(evaluate_id, output)
        finally:
            clear_context_evaluate()

    def stream_validate(self, evaluate_id, output, log = True, usage=1):
        if log:
            logger.debug(
                message = f"stream_validate payload - {output}",
                event = Event.STREAM_VALIDATE,
                properties = {
                    "evaluate_id": evaluate_id,
                },
                data = output
            )
        self.backend_cli.stream_validate(evaluate_id, output)
