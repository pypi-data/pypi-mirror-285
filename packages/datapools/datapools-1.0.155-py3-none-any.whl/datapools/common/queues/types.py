import json
from enum import Enum
from typing import Optional, Any, Dict, Union, List
from ..types import BaseMessage

# from ..logger import logger
MESSAGE_STUDY_URL_PRIORITY: int = 3
MESSAGE_HINT_URL_PRIORITY: int = 2
MESSAGE_BACK_TASK_PRIORITY: int = 1


class QueueRole(Enum):
    Publisher = 1
    Receiver = 2


class QueueMessageType(Enum):
    Task = 1
    ReportTaskStatus = 2  # to scheduler
    StorageInvalidation = 3
    Stop = 4
    ProcessIteration = 5
    DelayedTask = 6
    ReportEvaluation = 7  # to scheduler


class QueueMessage:
    type: QueueMessageType
    session_id: Optional[str] = None
    data: Optional[Union[BaseMessage, Dict[Any, Any]]] = None
    priority: Optional[int] = 0

    def __init__(self, message_type: QueueMessageType, data=None, session_id: Optional[str] = None, priority: int = 0):
        self.session_id = session_id
        self.type = message_type
        self.data = data
        self.priority = priority

    def encode(self):
        # logger.info( f'encoding {self.type=} {self.data=}')
        return json.dumps(
            {
                "session_id": self.session_id,
                "type": self.type.value,
                "data": json.dumps(self.data.to_dict() if isinstance(self.data, BaseMessage) else self.data),
            }
        ).encode()

    @staticmethod
    def decode(binary):
        j = json.loads(binary.decode())
        res = QueueMessage(
            session_id=j.get("session_id"), message_type=QueueMessageType(j["type"]), data=json.loads(j["data"])
        )
        return res


class QueueTopicMessage:
    topic: List[str]
    data: BaseMessage
    priority: Optional[int] = 0

    def __init__(self, topic: str, data: BaseMessage, priority: int = 0):
        self.topic = topic.split(".")
        self.data = data
        self.priority = priority

    def encode(self):
        # logger.info( f'encoding {self.type=} {self.data=}')
        return json.dumps({"data": json.dumps(self.data.to_dict())}).encode()

    @staticmethod
    def decode(topic, binary):
        j = json.loads(binary.decode())
        res = QueueTopicMessage(topic=topic, data=json.loads(j["data"]))
        return res
