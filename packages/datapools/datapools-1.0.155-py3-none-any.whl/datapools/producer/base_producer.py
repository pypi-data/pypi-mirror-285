import asyncio

# import importlib
# import inspect
import os

# import sys
import traceback

# from enum import Enum
from typing import List, Optional

from ..common.backend_api import BackendAPI, BackendAPIException
from ..common.logger import logger
from ..common.queues import GenericQueue, QueueMessage, QueueMessageType, QueueRole, QueueTopicMessage
from ..common.session_manager import SessionManager, Session, ContentStatus
from ..common.stoppable import Stoppable
from ..common.storage.file_storage import FileStorage
from ..common.types import (
    BaseProducerSettings,
    InvalidUsageException,
    SchedulerEvaluationReport,
    EvaluationStatus,
    WorkerEvaluationReport,
    ProducerTask,
)
from ..worker.utils import get_storage_invalidation_topic
from ..worker.worker import SessionFileStorage

# from .rules import DatapoolRulesChecker


class BaseProducer(Stoppable):
    cfg: BaseProducerSettings
    reports_queue: GenericQueue
    eval_queue: GenericQueue
    topics_queue: GenericQueue
    router_lock: asyncio.Lock

    def __init__(self, cfg: Optional[BaseProducerSettings] = None):
        super().__init__()
        self.cfg = cfg if cfg is not None else BaseProducerSettings()
        self.session_manager = SessionManager(self.cfg.REDIS_HOST, self.cfg.REDIS_PORT)

        if not self.cfg.CLI_MODE:
            self.api = BackendAPI(url=self.cfg.BACKEND_API_URL)

        self.router_lock = asyncio.Lock()

        # receives tasks from workers
        self.eval_queue = GenericQueue(
            role=QueueRole.Receiver,
            url=self.cfg.QUEUE_CONNECTION_URL,
            name=self.cfg.EVAL_TASKS_QUEUE_NAME,
        )
        logger.info("created receiver eval_tasks")

        # will invalidate worker cache entries
        self.topics_queue = GenericQueue(
            role=QueueRole.Publisher,
            url=self.cfg.QUEUE_CONNECTION_URL,
            name=self.cfg.TOPICS_QUEUE_NAME,
            topic=True,  # for Rabbitmq publisher
        )
        logger.info("created publisher worker_tasks")

        # sends reports to the scheduler
        self.reports_queue = GenericQueue(
            role=QueueRole.Publisher,
            url=self.cfg.QUEUE_CONNECTION_URL,
            name=self.cfg.REPORTS_QUEUE_NAME,
        )

        if self.cfg.CLI_MODE is True:
            self.stop_task_received = asyncio.Event()

        # self.datapool_rules_checker = DatapoolRulesChecker()

    async def run(self):
        self.tasks.append(asyncio.create_task(self.router_loop()))
        await self.eval_queue.run()
        await self.topics_queue.run()
        await self.reports_queue.run()
        await super().run()

    async def wait(self):
        if self.cfg.CLI_MODE is False:
            logger.error("baseproducer invalid usage")
            raise InvalidUsageException("not a cli mode")

        logger.info("BaseProducer wait()")
        await self.stop_task_received.wait()
        logger.info("BaseProducer stop_task_received")
        waiters = (
            self.eval_queue.until_empty(),
            self.topics_queue.until_empty(),
            self.reports_queue.until_empty(),
        )
        await asyncio.gather(*waiters)
        logger.info("BaseProducer wait done")

    async def stop(self):
        await self.eval_queue.stop()
        await self.topics_queue.stop()
        await self.reports_queue.stop()
        await super().stop()
        logger.info("BaseProducer stopped")

    async def router_loop(self):
        try:
            while not await self.is_stopped():
                async with self.router_lock:
                    message = await self.eval_queue.pop(timeout=0.2)
                    if message:
                        qm = QueueMessage.decode(message.body)
                        logger.info(f"{qm.session_id=}")
                        try:
                            session = await self.session_manager.get(qm.session_id)
                            if session is None or not await session.is_alive():
                                logger.info(f"session is deleted or stopped {qm.session_id=} {message.message_id}")
                                await self.eval_queue.mark_done(message)
                                continue

                            if qm.type == QueueMessageType.Task:
                                task = ProducerTask(**qm.data)
                                logger.info(f"Producer got: {task}")

                                session_storage = SessionFileStorage(self.cfg.WORKER_STORAGE_PATH, qm.session_id)
                                with session_storage.get_reader(task.storage_id) as raw_data_reader:
                                    await self.process_content(session, raw_data_reader, task)

                            elif qm.type == QueueMessageType.Stop:
                                logger.info("base_producer: stop task received")
                                self.stop_task_received.set()
                            else:
                                raise Exception(f"!!!!!!!!!!!!!!! BUG: unexpected {message=} {qm=}")

                            await self.eval_queue.mark_done(message)
                        except BackendAPIException as e:
                            logger.error("Catched BackendAPIException")
                            logger.error(traceback.format_exc())
                            await self.eval_queue.reject(message, requeue=True)
                            await asyncio.sleep(5)
                        except Exception as e:
                            logger.error("Catched Exception")
                            logger.error(traceback.format_exc())
                            await self.eval_queue.reject(message, requeue=False)
                            await self._report_evaluation(session, task, EvaluationStatus.Failure)

        except Exception as e:
            logger.error(f"Catched: {traceback.format_exc()}")
            logger.error(f"!!!!!!! Exception in Datapools::router_loop() {e}")

    async def process_content(self, session: Session, raw_data, task: ProducerTask):
        logger.info(f"BaseProducer::process_content {type(raw_data)=}")
        # path = os.path.join(self.cfg.STORAGE_PATH, str(datapool_id))
        if not self.is_shared_storage():
            path = self.cfg.STORAGE_PATH
            if not os.path.exists(path):  # type: ignore
                os.mkdir(path)  # type: ignore
            storage = FileStorage(path)
            # put data into persistent storage
            await storage.put(task.storage_id, raw_data)

        if await session.is_alive():  # session may have been stopped/deleted while processing content
            await self._report_evaluation(session, task, EvaluationStatus.Success)

    async def _report_evaluation(self, session: Session, task: ProducerTask, status: EvaluationStatus):
        await session.set_content_status(
            task.url,
            (
                ContentStatus.EVALUATION_SUCCESS
                if status == EvaluationStatus.Success
                else ContentStatus.EVALUATION_FAILURE
            ),
        )
        report = SchedulerEvaluationReport(status=status)
        await self.reports_queue.push(
            QueueMessage(session_id=session.id, message_type=QueueMessageType.ReportEvaluation, data=report)
        )
        await self.topics_queue.push(
            QueueTopicMessage(
                get_storage_invalidation_topic(task.worker_id),
                WorkerEvaluationReport(
                    url=task.url,
                    storage_id=task.storage_id,
                    session_id=session.id,
                    is_shared_storage=self.is_shared_storage(),
                    status=status,
                ),
            )
        )

    def is_shared_storage(self):
        return self.cfg.STORAGE_PATH is None or self.cfg.WORKER_STORAGE_PATH == self.cfg.STORAGE_PATH
