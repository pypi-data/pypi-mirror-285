from abc import ABCMeta, abstractmethod
import json
from time import sleep
from typing import List, Optional
from pydantic import BaseModel

from dalpha.backend_cli import BackendCli
from dalpha.logging import logger

class DataUpdateEvent(BaseModel):
    type: str
    timestamp: str
    payload: dict
    metadata: dict
    version: str

class S3File(BaseModel):
    url: str
    bucket: Optional[str]
    key: Optional[str]
    size: int

class DataUpdateItem(BaseModel):
    file: S3File

    def __str__(self):
        return self.model_dump_json()
    
def message_to_item(message) -> DataUpdateItem:
    payload = message.get("payload")
    return DataUpdateItem(
        file = S3File(
            url = payload.get("file").get("url"),
            bucket = payload.get("file").get("bucket"),
            key = payload.get("file").get("key"),
            size = payload.get("file").get("size"),
        )
    )

class DataUpdateConsumer(metaclass=ABCMeta):
    @abstractmethod
    def poll(self, records: int = 1, timeout_ms: int = 5000) -> List[DataUpdateItem]:
        pass

    @abstractmethod
    def commit(self):
        pass

    @abstractmethod
    def close(self):
        pass

class SqsDataUpdateConsumer(DataUpdateConsumer):
    def __init__(self, queue_url: str):
        import boto3
        self.sqs_consumer = boto3.client('sqs', region_name='ap-northeast-2')
        self.queue_url = queue_url
        self.receipt_handle = None

    def poll(self, records: int = 1) -> List[DataUpdateItem]:
        # sqs로부터 메시지를 가져옴
        response = self.sqs_consumer.receive_message(
            QueueUrl = self.queue_url,
            MaxNumberOfMessages = records  # 가져올 메시지의 최대 수 (1개 이상 설정 가능)
        )
        data_update_items = []
        messages = response.get('Messages', [])
        # invalid message를 제외한 message를 evaluate_items에 추가
        for message in messages:
            message_body = message['Body']
            try:
                # message_body를 딕셔너리로 변환
                message_dict = json.loads(message_body)
                self.receipt_handle = message['ReceiptHandle']
                data_update_items.append(message_to_item(message_dict))
            except json.JSONDecodeError:
                logger.error("유효한 JSON 형식이 아닙니다.")

        return data_update_items

    def commit(self):
        try: 
            self.sqs_consumer.delete_message(
                QueueUrl = self.queue_url,
                ReceiptHandle = self.receipt_handle
            )
        except Exception as e:
            logger.error(f"error from sqs.delete_message\n{e}")
            self.receipt_handle = None

    def close(self):
        self.sqs_consumer.close()

class KafkaDataUpdateConsumer(DataUpdateConsumer):
    def __init__(self, api_id: int, backend_cli: BackendCli, kafka_topic: str):
        self.kafka_topic = kafka_topic
        from dalpha.kafka_cli import get_consumer
        self.kafka_consumer = get_consumer(self.kafka_topic, api_id)
        self.backend_cli = backend_cli


    def poll(self, records: int = 1, timeout_ms: int = 5000) -> List[DataUpdateItem]:
        try:
            #print(self.kafka_consumer.beginning_offsets(partitions))
            record = self.kafka_consumer.poll(
                timeout_ms=timeout_ms,
                max_records=records,
                update_offsets=False,
            )
            logger.info(f"polled record: {record}")
            sleep(10)
            
            ret = []
            # 1개만 받아온 경우
            v = record.values()
            for messages in v:
                if not isinstance(messages, list):
                    logger.error(f"unexpected kafka message format: {type(message)}")
                    break
                for message in messages:
                    try:
                        event = json.loads(message.value.decode('utf-8'))
                        ret.append(message_to_item(event))
                    except json.JSONDecodeError:
                        # TODO: 현재 로직이면 이 경우 offset skip 됨, 잘못된 동작은 아닌 듯 하나 체크 필요
                        logger.error("유효한 JSON 형식이 아닙니다.")

            return ret
        except Exception as e:
            logger.error(f"error from kafka poll\n{e}")
            return []

    def commit(self):
        try:
            self.kafka_consumer.commit()
        except Exception as e:
            print(e)
            logger.error(f"error from kafka commit\n{e}")
        
    def close(self):
        self.kafka_consumer.close()
