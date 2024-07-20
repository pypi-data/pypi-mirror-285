import json
from abc import abstractmethod
from enum import Enum, IntEnum
from typing import Any, List, NamedTuple, Optional, TypeAlias, Union

from pydantic import AnyUrl, BaseModel
from pydantic_settings import BaseSettings

# from .storage import FileStorage

DEFAULT_WORKER_STUDY_URL_TASKS_R_QUEUE_NAME = "worker_study_url_r"
DEFAULT_WORKER_STUDY_URL_TASKS_W_QUEUE_NAME = "worker_study_url_w"
DEFAULT_QUEUE_WORKER_HP_TASKS = "worker_hp_tasks"
DEFAULT_QUEUE_WORKER_LP_TASKS = "worker_lp_tasks"
# DEFAULT_QUEUE_DELAYED_WORKER_TASKS = "delayed_worker_tasks"
DEFAULT_QUEUE_REPORTS = "worker_reports"
DEFAULT_QUEUE_EVAL_TASKS = "eval_tasks"
DEFAULT_QUEUE_TOPICS = "topics"

DEFAULT_RABBITMQ_HOST = "rabbitmq.openlicense"
DEFAULT_RABBITMQ_PORT: int = 5672
DEFAULT_REDIS_HOST = "redis.openlicense"
DEFAULT_REDIS_PORT: int = 6379

DEFAULT_CONNECTION_URL: str = "amqp://guest:guest@{host}:{port}/".format(
    host=DEFAULT_RABBITMQ_HOST, port=DEFAULT_RABBITMQ_PORT
)

DEFAULT_BACKEND_API_URL: str = "https://openlicense.ai/internal/"
DEFAULT_BACKEND_HINTS_PERIOD: int = 10  # seconds
DEFAULT_POSTPONED_RETRY_PERIOD: int = 30

DEFAULT_MAX_STUDY_URL_PROCESSING_TASKS: int = 3
DEFAULT_MAX_HIGH_PRIORITY_PROCESSING_TASKS: int = 7
DEFAULT_MAX_LOW_PRIORITY_PROCESSING_TASKS: int = 3

DEFAULT_MAX_TASKS_SLEEP: float = 3

# DEFAULT_STUDY_URL_TASK_WAIT_TIMEOUT: float = 3
# DEFAULT_HP_TASK_WAIT_TIMEOUT: float = 1
# DEFAULT_LP_TASK_WAIT_TIMEOUT: float = 0.2


class InvalidUsageException(Exception):
    pass


class SerializableModel(BaseModel):
    # model_config = ConfigDict(use_enum_values=True)
    pass


class BaseCrawlerSettings(BaseSettings):
    def fload(self, json_path):
        """fills self using json file path"""
        with open(json_path, "r") as fp:
            config = json.load(fp)  # expects dict output
            self.load(config)

    @abstractmethod
    def load(self, config: dict): ...


DONT_RETRY = -1


class SchedulerSettings(BaseCrawlerSettings):
    QUEUE_CONNECTION_URL: str = DEFAULT_CONNECTION_URL
    BACKEND_API_URL: str = DEFAULT_BACKEND_API_URL
    BACKEND_HINTS_PERIOD: int = DEFAULT_BACKEND_HINTS_PERIOD
    POSTPONED_RETRY_PERIOD: int = DEFAULT_POSTPONED_RETRY_PERIOD
    POSTPONED_MAX_RETRIES: int = 0  # 0 - retry until success, -1 - no retries

    REDIS_HOST: str = DEFAULT_REDIS_HOST
    REDIS_PORT: int = DEFAULT_REDIS_PORT
    # cli settings
    CLI_MODE: bool = False

    WORKER_TASKS_QUEUE_NAME: str = DEFAULT_QUEUE_WORKER_HP_TASKS
    REPORTS_QUEUE_NAME: str = DEFAULT_QUEUE_REPORTS

    MAX_COMPLETE_TASKS: Optional[int] = None  # hard limit for faster testing
    MAX_EMPTY_COMPLETE_TASKS: Optional[int] = None

    def load(self, config: dict):
        """fills self with json config"""
        # Stop criteria
        stop_criteria = config.get("stop_criteria", {})
        self.MAX_EMPTY_COMPLETE_TASKS = stop_criteria.get("max_empty_complete_tasks")

        postponed = config.get("postponed", {})
        retry_period = postponed.get("retry_period", 0)
        if retry_period:
            self.POSTPONED_RETRY_PERIOD = int(retry_period)
        max_retries = postponed.get("max_retries")
        if max_retries is not None:
            self.POSTPONED_MAX_RETRIES = int(max_retries)

        # Queue
        queue = config.get("queue", {})
        queue_connection_url = queue.get("connection_url")
        if queue_connection_url is not None:
            self.QUEUE_CONNECTION_URL = queue_connection_url

        self.WORKER_TASKS_QUEUE_NAME = queue.get("worker_tasks_queue_name", DEFAULT_QUEUE_WORKER_HP_TASKS)
        self.REPORTS_QUEUE_NAME = queue.get(
            "worker_reports_queue_name", DEFAULT_QUEUE_REPORTS
        )  # TODO: replace worker_reports_queue_name with reports_queue_name in config.json

        # Backend
        backend = config.get("backend", {})
        api_url = backend.get("api_url")
        if api_url is not None:
            self.BACKEND_API_URL = api_url
        hints_period = backend.get("hints_period")
        if hints_period is not None:
            self.BACKEND_HINTS_PERIOD = hints_period

        # Redis
        redis = config.get("redis", {})
        redis_host = redis.get("host")
        if redis_host is not None:
            self.REDIS_HOST = redis_host
        redis_port = redis.get("port")
        if redis_port is not None:
            self.REDIS_PORT = redis_port


class WorkerSettings(BaseCrawlerSettings):
    QUEUE_CONNECTION_URL: str = DEFAULT_CONNECTION_URL
    MAX_STUDY_URL_PROCESSING_TASKS: int = DEFAULT_MAX_STUDY_URL_PROCESSING_TASKS
    MAX_HIGH_PRIORITY_PROCESSING_TASKS: int = DEFAULT_MAX_HIGH_PRIORITY_PROCESSING_TASKS
    MAX_LOW_PRIORITY_PROCESSING_TASKS: int = DEFAULT_MAX_LOW_PRIORITY_PROCESSING_TASKS
    MAX_PLUGIN_INSTANCES_DEFAULT: int = 1
    MAX_TASKS_SLEEP: float = DEFAULT_MAX_TASKS_SLEEP
    # STUDY_URL_TASK_WAIT_TIMEOUT: float = DEFAULT_STUDY_URL_TASK_WAIT_TIMEOUT
    # HP_TASK_WAIT_TIMEOUT: float = DEFAULT_HP_TASK_WAIT_TIMEOUT
    # LP_TASK_WAIT_TIMEOUT: float = DEFAULT_LP_TASK_WAIT_TIMEOUT

    ATTEMPTS_PER_URL: int = 3
    ATTEMPTS_DELAY: int = 5  # seconds
    DELAYED_TASK_REDO_PERIOD: int = 20  # seconds
    STORAGE_PATH: str = "/storage/"

    REDIS_HOST: str = DEFAULT_REDIS_HOST
    REDIS_PORT: int = DEFAULT_REDIS_PORT

    WORKER_STUDY_URL_TASKS_R_QUEUE_NAME: str = DEFAULT_WORKER_STUDY_URL_TASKS_R_QUEUE_NAME
    WORKER_STUDY_URL_TASKS_W_QUEUE_NAME: str = DEFAULT_WORKER_STUDY_URL_TASKS_W_QUEUE_NAME
    WORKER_HP_TASKS_QUEUE_NAME: str = DEFAULT_QUEUE_WORKER_HP_TASKS
    WORKER_LP_TASKS_QUEUE_NAME: str = DEFAULT_QUEUE_WORKER_LP_TASKS
    # DELAYED_WORKER_TASKS_QUEUE_NAME: str = DEFAULT_QUEUE_DELAYED_WORKER_TASKS
    REPORTS_QUEUE_NAME: str = DEFAULT_QUEUE_REPORTS
    EVAL_TASKS_QUEUE_NAME: str = DEFAULT_QUEUE_EVAL_TASKS
    TOPICS_QUEUE_NAME: str = DEFAULT_QUEUE_TOPICS

    # None: access is configured on AWS, bucket is NOT PUBLIC
    # "": bucket is PUBLIC
    # S3_IMAGESHACK_ACCESS_KEY: Optional[str] = None
    # S3_IMAGESHACK_ACCESS_SECRET: Optional[str] = None

    # GOOGLE_DRIVE_API_KEY: str = ""
    BACKEND_API_URL: str = DEFAULT_BACKEND_API_URL

    CLI_MODE: bool = False

    USE_ONLY_PLUGINS: Optional[List[str]] = None
    ADDITIONAL_PLUGINS: Optional[List[str]] = None

    plugins_config: dict = {}

    def load(self, config: dict):
        """fills self with json config"""
        backend = config.get("backend", {})
        api_url = backend.get("api_url")
        if api_url is not None:
            self.BACKEND_API_URL = api_url

        # Queue
        queue = config.get("queue", {})
        queue_connection_url = queue.get("connection_url")
        if queue_connection_url is not None:
            self.QUEUE_CONNECTION_URL = queue_connection_url

        self.MAX_STUDY_URL_PROCESSING_TASKS = queue.get("max_study_url_tasks", DEFAULT_MAX_STUDY_URL_PROCESSING_TASKS)
        self.MAX_HIGH_PRIORITY_PROCESSING_TASKS = queue.get("max_lp_tasks", DEFAULT_MAX_HIGH_PRIORITY_PROCESSING_TASKS)
        self.MAX_LOW_PRIORITY_PROCESSING_TASKS = queue.get("max_lp_tasks", DEFAULT_MAX_LOW_PRIORITY_PROCESSING_TASKS)
        self.MAX_TASKS_SLEEP = queue.get("max_tasks_sleep", DEFAULT_MAX_TASKS_SLEEP)
        # self.STUDY_URL_TASK_WAIT_TIMEOUT = queue.get("study_url_task_wait_timeout", DEFAULT_STUDY_URL_TASK_WAIT_TIMEOUT)
        # self.HP_TASK_WAIT_TIMEOUT = queue.get("hp_task_wait_timeout", DEFAULT_HP_TASK_WAIT_TIMEOUT)
        # self.LP_TASK_WAIT_TIMEOUT = queue.get("lp_task_wait_timeout", DEFAULT_LP_TASK_WAIT_TIMEOUT)

        self.WORKER_STUDY_URL_TASKS_R_QUEUE_NAME = queue.get(
            "worker_study_url_tasks_r_queue_name", DEFAULT_WORKER_STUDY_URL_TASKS_R_QUEUE_NAME
        )
        self.WORKER_STUDY_URL_TASKS_W_QUEUE_NAME = queue.get(
            "worker_study_url_tasks_w_queue_name", DEFAULT_WORKER_STUDY_URL_TASKS_W_QUEUE_NAME
        )
        self.WORKER_HP_TASKS_QUEUE_NAME = queue.get("worker_hp_tasks_queue_name", DEFAULT_QUEUE_WORKER_HP_TASKS)
        self.WORKER_LP_TASKS_QUEUE_NAME = queue.get("worker_lp_tasks_queue_name", DEFAULT_QUEUE_WORKER_LP_TASKS)
        self.REPORTS_QUEUE_NAME = queue.get(
            "worker_reports_queue_name", DEFAULT_QUEUE_REPORTS
        )  # replace worker_reports_queue_name with reports_queue_name in config.json
        self.EVAL_TASKS_QUEUE_NAME = queue.get("eval_tasks_queue_name", DEFAULT_QUEUE_EVAL_TASKS)
        self.TOPICS_QUEUE_NAME = queue.get("topics_queue_name", DEFAULT_QUEUE_TOPICS)

        # redis
        redis = config.get("redis", {})
        redis_host = redis.get("host")
        if redis_host is not None:
            self.REDIS_HOST = redis_host
        redis_port = redis.get("port")
        if redis_port is not None:
            self.REDIS_PORT = redis_port

        # Storage
        storage = config.get("storage", {})
        worker_storage = storage.get("worker", {})
        storage_path = worker_storage.get("path")
        if storage_path is not None:
            self.STORAGE_PATH = storage_path

        # plugins
        self.plugins_config = config.get("plugins", {})


class BaseProducerSettings(BaseCrawlerSettings):
    QUEUE_CONNECTION_URL: str = DEFAULT_CONNECTION_URL
    BACKEND_API_URL: str = DEFAULT_BACKEND_API_URL
    STORAGE_PATH: Optional[str] = None
    WORKER_STORAGE_PATH: str = "/worker_storage/"

    REDIS_HOST: str = DEFAULT_REDIS_HOST
    REDIS_PORT: int = DEFAULT_REDIS_PORT

    CLI_MODE: bool = False

    EVAL_TASKS_QUEUE_NAME: str = DEFAULT_QUEUE_EVAL_TASKS
    TOPICS_QUEUE_NAME: str = DEFAULT_QUEUE_TOPICS
    REPORTS_QUEUE_NAME: str = DEFAULT_QUEUE_REPORTS

    def load(self, config: dict):
        """fills self with json config"""
        backend = config.get("backend", {})
        api_url = backend.get("api_url")
        if api_url is not None:
            self.BACKEND_API_URL = api_url

        # Queue
        queue = config.get("queue", {})
        queue_connection_url = queue.get("connection_url")
        if queue_connection_url is not None:
            self.QUEUE_CONNECTION_URL = queue_connection_url

        self.EVAL_TASKS_QUEUE_NAME = queue.get("eval_tasks_queue_name", DEFAULT_QUEUE_EVAL_TASKS)
        self.TOPICS_QUEUE_NAME = queue.get("topics_queue_name", DEFAULT_QUEUE_TOPICS)

        # redis
        redis = config.get("redis", {})
        redis_host = redis.get("host")
        if redis_host is not None:
            self.REDIS_HOST = redis_host
        redis_port = redis.get("port")
        if redis_port is not None:
            self.REDIS_PORT = redis_port

        # Storage
        storage = config.get("storage", {})
        worker_storage = storage.get("worker", {})
        storage_path = worker_storage.get("path")
        if storage_path is not None:
            self.WORKER_STORAGE_PATH = storage_path
        producer_storage = storage.get("producer", {})
        storage_path = producer_storage.get("path")
        if storage_path is not None:
            self.STORAGE_PATH = storage_path


class CrawlerHintURLStatus(IntEnum):
    Unprocessed = 0
    Success = 1
    Failure = 2
    Processing = 3
    Rejected = 4
    Canceled = 5
    Restarted = 6


class CrawlerHintURL(BaseModel):
    url: AnyUrl
    id: Optional[int] = 0
    status: Optional[CrawlerHintURLStatus] = CrawlerHintURLStatus.Unprocessed
    session_id: Optional[str] = None


class DatapoolContentType(str, Enum):
    Text = "Text"
    Image = "Image"
    Video = "Video"
    Audio = "Audio"

    def __hash__(self):
        if self.value == DatapoolContentType.Text:
            return 1
        if self.value == DatapoolContentType.Image:
            return 2
        if self.value == DatapoolContentType.Video:
            return 3
        if self.value == DatapoolContentType.Audio:
            return 4
        raise Exception(f"Not supported DatapoolContentType __hash__ {self.value}")


class BaseMessage(BaseModel):
    def to_dict(self):
        res = self.__dict__
        return res


class WorkerTask(BaseMessage):
    url: str
    content_type: Optional[DatapoolContentType] = None
    status: Optional[CrawlerHintURLStatus] = None


class StudyUrlTask(BaseMessage):
    url: str
    receiver_routing_id: str
    request_id: str
    max_depth: int


class StudyUrlResponse(BaseMessage):
    request_id: str
    status: bool
    tags: Optional[List[str]] = None


class ProducerTask(BaseMessage):
    parent_url: str
    url: str
    worker_id: str
    storage_id: str
    tag_id: Optional[str] = None
    tag_keepout: Optional[bool] = False
    copyright_tag_id: Optional[str] = None
    copyright_tag_keepout: Optional[bool] = False
    platform_tag_id: Optional[str] = None
    platform_tag_keepout: Optional[bool] = False
    type: Optional[DatapoolContentType] = None
    priority_timestamp: Optional[int] = None


class DelayedWorkerTask(WorkerTask):
    timestamp: int


class EvaluationStatus(IntEnum):
    Success = 1
    Failure = 2


class SchedulerEvaluationReport(BaseMessage):
    status: EvaluationStatus


class WorkerEvaluationReport(BaseMessage):
    url: str
    storage_id: str
    is_shared_storage: bool
    session_id: str
    status: EvaluationStatus


class BaseCrawlerResult(BaseMessage):
    pass


class CrawlerContent(BaseCrawlerResult):
    tag_id: Optional[str] = None
    tag_keepout: Optional[bool] = False
    copyright_tag_id: Optional[str] = None
    copyright_tag_keepout: Optional[bool] = False
    platform_tag_id: Optional[str] = None
    platform_tag_keepout: Optional[bool] = False
    type: Optional[DatapoolContentType] = None
    # storage_id: Any
    url: Union[str, AnyUrl]
    priority_timestamp: Optional[int] = None
    content: Optional[Any] = None

    def to_dict(self):
        res = self.__dict__
        res["type"] = res["type"].value
        return res


class CrawlerBackTask(BaseCrawlerResult):
    url: str


class CrawlerDemoUser(BaseCrawlerResult):
    user_name: str
    short_tag_id: str
    platform: str


class CrawlerNop(BaseCrawlerResult):
    pass
