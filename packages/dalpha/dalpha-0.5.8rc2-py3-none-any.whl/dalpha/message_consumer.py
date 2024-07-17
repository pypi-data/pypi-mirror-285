import json
import os
import time
from typing import Optional
from dalpha.backend_cli import BackendCli
from dalpha.logging import logger
from pydantic import BaseModel
from abc import ABCMeta, abstractmethod
from typing import List

from dalpha.logging.events import Event

class EvaluateItem(BaseModel):
    id: int
    evaluateGroupId: Optional[int]
    accountId: int
    inferenceApiId: int
    key: str
    metadata : dict

    def __str__(self):
        return self.model_dump_json()

def to_evaluate_item(message):
    return EvaluateItem(
        id = message.get("id"),
        evaluateGroupId = message.get("evaluateGroupId"),
        accountId = message.get("accountId"),
        inferenceApiId = message.get("inferenceApiId"),
        key = message.get("key"),
        metadata = message.get("metadata")
    )

class MessageConsumer(metaclass=ABCMeta):
    @abstractmethod
    def poll(self, records: int = 1, timeout_ms: int = 5000) -> List[EvaluateItem]:
        pass

    @abstractmethod
    def commit(self, id):
        pass

    @abstractmethod
    def close(self):
        pass

class KafkaMessageConsumer(MessageConsumer):
    def __init__(self, api_id: int, backend_cli: BackendCli, kafka_topic: str):
        self.kafka_topic = kafka_topic
        from dalpha.kafka_cli import get_consumer
        self.kafka_consumer = get_consumer(self.kafka_topic, api_id)
        self.backend_cli = backend_cli

    def poll(self, records: int = 1, timeout_ms: int = 5000) -> List[EvaluateItem]:
        record = self.kafka_consumer.poll(
            timeout_ms=timeout_ms,
            max_records=records,
            update_offsets=False,
        )
        
        ret = []
        # 1개만 받아온 경우
        v = record.values()
        for messages in v:
            if not isinstance(messages, list):
                logger.error(f"unexpected kafka message format: {type(message)}")
                break
            for message in messages:
                try:
                    message_dict = json.loads(message.value.decode('utf-8'))
                    evaluate = self.backend_cli.get_evaluate(message_dict.get('id'))
                    if evaluate != None:
                        ret.append(to_evaluate_item(evaluate))
                except json.JSONDecodeError:
                    # TODO: 현재 로직이면 이 경우 offset skip 됨, 잘못된 동작은 아닌 듯 하나 체크 필요
                    logger.error("유효한 JSON 형식이 아닙니다.")

        return ret

    def commit(self, id):
        try:
            self.kafka_consumer.commit()
        except Exception as e:
            logger.error(f"error from kafka commit\n{e}")
        
    def close(self):
        self.kafka_consumer.close()

class SqsMessageConsumer(MessageConsumer):
    def __init__(self, api_id: int, backend_cli: BackendCli, queue_url: str):
        import boto3
        self.sqs_consumer = boto3.client('sqs', region_name='ap-northeast-2')
        self.queue_url = queue_url
        self.backend_cli = backend_cli
        self.evaluates = {}

    def _batch(self, iterable, n):
        # Yield successive n-sized chunks from iterable.
        for i in range(0, len(iterable), n):
            yield iterable[i:i + n]

    def _delete_messages(self, evaluate_ids):
        '''
            evaluate_id를 10개씩 끊어서 sqs에 batch delete 요청으로 메세지 삭제
        '''
        entries = list(map(lambda evaluate_id: {
            'Id': str(evaluate_id),
            'ReceiptHandle': self.evaluates[evaluate_id]
        }, evaluate_ids))
        for group in self._batch(entries, 10):
            try:
                self.sqs_consumer.delete_message_batch(
                    QueueUrl = self.queue_url,
                    Entries = group
                )
            except Exception as e:
                logger.error(f"Error while deleting messages\n{e}")

    def poll(self, records: int = 1) -> List[EvaluateItem]:
        # sqs로부터 메시지를 가져옴
        response = self.sqs_consumer.receive_message(
            QueueUrl = self.queue_url,
            MaxNumberOfMessages = records  # 가져올 메시지의 최대 수 (1개 이상 설정 가능)
        )
        evaluate_items = []
        invalid_messages = []
        messages = response.get('Messages', [])
        # invalid message를 제외한 message를 evaluate_items에 추가
        for message in messages:
            message_body = message['Body']
            try:
                # message_body를 딕셔너리로 변환
                message_dict = json.loads(message_body)
                self.evaluates[message_dict['id']] = message['ReceiptHandle']
                evaluate = self.backend_cli.get_evaluate(message_dict.get('id'))
                if evaluate != None:
                    evaluate_items.append(to_evaluate_item(evaluate))
                else:
                    invalid_messages.append(message_dict)
            except json.JSONDecodeError:
                logger.error("유효한 JSON 형식이 아닙니다.")

        # sqs에서 invalid messages 삭제
        if (len(invalid_messages) > 0):
            try:
                self._delete_messages(list(map(lambda x: x['id'], invalid_messages)))
                logger.info(
                    message = f"Deleted {len(invalid_messages)} invalid messages: {invalid_messages}"
                )
            except Exception as e:
                logger.error(f"Error while validating evaluate message\n{e}", event = Event.POLL)

        return evaluate_items

    def commit(self, id):
        try: 
            self.sqs_consumer.delete_message(
                QueueUrl = self.queue_url,
                ReceiptHandle = self.evaluates[id]
            )
        except Exception as e:
            logger.error(f"error from sqs.delete_message\n{e}")
            del self.evaluates[id]

    def close(self):
        self.sqs_consumer.close()

class RawMessageConsumer(MessageConsumer):
    def __init__(self, api_id: int, backend_cli: BackendCli, **kwargs):
        self.api_id = api_id
        self.token = kwargs.get("token")
        self.backend_cli = backend_cli
        

    def poll(self, records: int = 1, timeout_ms: int = 5000) -> List[EvaluateItem]:
        time.sleep(0.2)
        poll_result = self.backend_cli.poll()
        if poll_result:  
            logger.info(
                message = "return poll item",
                event = Event.POLL,
                data = poll_result
            )
            return [to_evaluate_item(poll_result)]
        else:
            return []

    def commit(self, id):
        pass

    def close(self):
        pass
