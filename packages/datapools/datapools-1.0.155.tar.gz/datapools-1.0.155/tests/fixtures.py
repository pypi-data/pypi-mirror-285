import asyncio
import logging
from pytest import fixture

from datapools.common.session_manager import Session, SessionManager, SessionStatus, URLState
from datapools.common.types import WorkerSettings, CrawlerHintURLStatus
from datapools.common.logger import setup_logger


@fixture()
def setup():
    logging.info("SETUP")
    setup_logger()


@fixture()
def worker_settings(setup):
    return WorkerSettings()


@fixture()
async def session_manager(worker_settings) -> SessionManager:
    res = SessionManager(worker_settings.REDIS_HOST)
    yield res
    await res.stop()


@fixture()
async def session(session_manager) -> Session:
    res = await session_manager.create(1)
    yield res
    await session_manager.remove(res.id)
