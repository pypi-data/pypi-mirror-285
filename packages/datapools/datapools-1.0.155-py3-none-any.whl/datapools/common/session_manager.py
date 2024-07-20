import time
import json
from enum import Enum, IntEnum
from hashlib import md5 as h_md5
from typing import List, Optional
from pydantic import BaseModel, AnyUrl

from redis.asyncio import Redis, ConnectionError as RedisConnectionError

from .logger import logger
from .types import CrawlerHintURLStatus

# from ..logger import logger
SESSION_VERSION = 1

SESSION_METADATA_KEY_PREFIX = "crawler_session_meta_"  # hash
SESSION_URLS_KEY_PREFIX = "crawler_session_urls_"  # hash: md5(WorkerTask.url) => URLState
SESSION_CONTENT_KEY_PREFIX = "crawler_session_content_"  # set: md5(CrawlerContent.url) => ContentState
SESSION_TAGS_USAGE_KEY_PREFIX = "crawler_session_tags_usage_"  # hash: tag_id => count
SESSION_HEARTBEAT_KEY_PREFIX = "crawler_session_heartbeat_"  # hash: worker_id => last hearbeat timestamp
# POSTPONED_SESSIONS_KEY = "crawler_postponed_sessions"  # set


class URLState(BaseModel):
    worker_id: str = ""
    status: CrawlerHintURLStatus


class ContentStatus(IntEnum):
    DOWNLOAD_SUCCESS = 1
    DOWNLOAD_INVALID = 2
    EVALUATION_SUCCESS = 3
    EVALUATION_FAILURE = 4


class ContentState(BaseModel):
    worker_id: str = ""
    status: ContentStatus
    storage_id: Optional[str] = None


class SessionStatus(IntEnum):
    NORMAL = 0
    STOPPED = 1
    # POSTPONED = 2


def md5(data: str | bytes) -> str:
    if isinstance(data, str):
        data = data.encode()
    return h_md5(data).hexdigest()


class Session:
    id: str
    r: Redis
    meta_key: str
    urls_key: str
    content_key: str
    tags_usage_key: str
    heartbeat_key: str
    stats_channel: str

    def __init__(self, session_id, redis_inst: Redis):
        self.id = session_id
        self.r = redis_inst
        self.meta_key = SessionManager.get_meta_key(self.id)
        self.urls_key = SessionManager.get_urls_key(self.id)
        self.content_key = SessionManager.get_content_key(self.id)
        self.tags_usage_key = SessionManager.get_tags_usage_key(self.id)
        self.heartbeat_key = SessionManager.get_heartbeat_key(self.id)
        self.stats_channel = Session.get_stats_channel(self.id)

    @staticmethod
    def get_stats_channel(session_id_or_mask):
        return f"stats_channel_{session_id_or_mask}"

    @staticmethod
    def get_stats_channel_mask():
        return Session.get_stats_channel("*")

    @staticmethod
    def get_session_id_by_channel(channel_name):
        return channel_name[14:]

    async def _get_meta_v(self):
        raw = await self.r.hgetall(self.meta_key)
        version = int(raw[b"version"]) if b"version" in raw else 0
        return (raw, version)

    async def get_meta(self):
        (raw, version) = await self._get_meta_v()
        res = {
            "hint_id": raw[b"hint_id"].decode(),
            "url": raw[b"url"].decode(),
            "total_urls": int(raw[b"total_urls"]),
            "complete_urls": int(raw[b"complete_urls"]),
            "failed_urls": int(raw[b"failed_urls"]),
            "rejected_urls": int(raw[b"rejected_urls"]),
            "crawled_content": int(raw[b"crawled_content"]),
            "evaluated_content": int(raw[b"evaluated_content"]),
            "failed_content": int(raw[b"failed_content"]),
            "status": int(raw[b"status"]),
            "last_reported_status": (
                CrawlerHintURLStatus(int(raw[b"last_reported_status"]))
                if b"last_reported_status" in raw
                else CrawlerHintURLStatus.Unprocessed
            ),
        }
        # if version >= 1:
        #     res["last_postponed"] = int(raw[b"last_postponed"])
        #     res["total_postponed"] = int(raw[b"total_postponed"])

        return res

    async def is_valid(self):
        (raw, version) = await self._get_meta_v()
        if version < SESSION_VERSION:
            return False
        keys = [
            b"hint_id",
            b"url",
            b"total_urls",
            b"complete_urls",
            b"failed_urls",
            b"rejected_urls",
            b"crawled_content",
            b"evaluated_content",
            b"failed_content",
            b"status",
        ]
        return all(k in raw for k in keys)

    async def set_status(self, status: SessionStatus):
        await self.r.hset(self.meta_key, "status", status.value)

    async def get_status(self) -> SessionStatus:
        status = await self.r.hget(self.meta_key, "status")
        if status is not None:
            return SessionStatus(int(status))
        raise Exception("invalid session")

    async def restart(self):
        # crawled_content = 0
        # evaluated_content = 0
        # cursor = 0
        # while True:
        #     res = await self.r.hscan(self.urls_key, cursor, count=100)
        #     # logger.info(f"hscan {res=}")
        #     for __url, raw_state in res[1].items():
        #         url_state = json.loads(raw_state.decode())
        #         url_state = URLState(**url_state)
        #         if url_state.status == URLStatus.DOWNLOADED:
        #             crawled_content += 1
        #         elif url_state.status == URLStatus.EVALUATED:
        #             evaluated_content += 1
        #     cursor = res[0]
        #     if cursor == 0:
        #         break

        await self.r.hset(self.meta_key, "total_urls", 0)
        await self.r.hset(self.meta_key, "complete_urls", 0)
        await self.r.hset(self.meta_key, "failed_urls", 0)
        await self.r.hset(self.meta_key, "rejected_urls", 0)
        # await self.r.hset(self.meta_key, "crawled_content", crawled_content)
        # await self.r.hset(self.meta_key, "evaluated_content", evaluated_content)
        await self.r.hset(self.meta_key, "failed_content", 0)
        await self.r.hset(self.meta_key, "since_last_tagged", 0)

        await self.r.delete(self.urls_key)

        await self.set_status(SessionStatus.NORMAL)

    async def is_stopped(self):
        status = await self.get_status()
        return status == SessionStatus.STOPPED

    async def is_alive(self):
        return await self.exists() and await self.get_status() != SessionStatus.STOPPED

    async def add_url(self, url):
        # urls are stored in sets
        res = await self.set_url_state(url, URLState(status=CrawlerHintURLStatus.Unprocessed))
        if res:
            await self.r.hincrby(self.meta_key, "total_urls", 1)
        return res == 1

    async def has_url(self, url: AnyUrl | str):
        res = await self.r.hexists(self.urls_key, md5(str(url)))
        # logger.info( f'has_url {res=} {type(res)=}')
        return res

    async def get_url_state(self, url: AnyUrl | str) -> URLState | None:
        res = await self.r.hget(self.urls_key, md5(str(url)))
        if res is not None:
            res = json.loads(res.decode())
            res = URLState(**res)
        return res

    async def set_url_state(self, url: AnyUrl | str, state: URLState):
        data = state.model_dump(mode="json")
        return await self.r.hset(self.urls_key, md5(str(url)), json.dumps(data))

    async def get_url_worker(self, url: AnyUrl | str) -> str | None:
        res = await self.get_url_state(str(url))
        return res.worker_id if res is not None else None

    async def set_url_worker(self, url: AnyUrl | str, worker_id: str):
        state = await self.get_url_state(str(url))
        if state is not None:
            state.worker_id = worker_id
            await self.set_url_state(url, state)

    async def set_url_status(self, url: AnyUrl | str, status: CrawlerHintURLStatus):
        state = await self.get_url_state(str(url))
        if state is not None:
            state.status = status

            logger.info(f"set_url_status {state=}")
            await self.set_url_state(url, state)

    # async def get_content_status(self, url: AnyUrl | str) -> ContentStatus:
    #     state = await self.get_content_state(str(url))
    #     return state.status if state is not None else None

    async def get_content_state(self, url: AnyUrl | str) -> ContentState | None:
        res = await self.r.hget(self.content_key, md5(str(url)))
        if res is not None:
            res = json.loads(res.decode())
            res = ContentState(**res)
        return res

    async def set_content_state(self, url: AnyUrl | str, state: ContentState):
        data = state.model_dump(mode="json")
        return await self.r.hset(self.content_key, md5(str(url)), json.dumps(data))

    async def set_content_status(self, url: AnyUrl | str, status: ContentStatus, storage_id: Optional[str] = None):
        state = await self.get_content_state(str(url))
        if state is None:
            raise Exception(f"No content state for {url=}")
        state.status = status
        state.storage_id = storage_id if status == ContentStatus.DOWNLOAD_SUCCESS else state.storage_id

        logger.info(f"set_content_status {state=} {storage_id=}")
        await self.set_content_state(url, state)

    async def all_urls_processed(self) -> bool:
        cursor = 0
        while True:
            res = await self.r.hscan(self.urls_key, cursor, count=100)
            # logger.info(f"hscan {res=}")
            for __url_md5, raw_state in res[1].items():
                url_state = json.loads(raw_state.decode())
                url_state = URLState(**url_state)
                if url_state.status in (CrawlerHintURLStatus.Unprocessed, CrawlerHintURLStatus.Processing):
                    return False
            cursor = res[0]
            if cursor == 0:
                break
        return True

    async def all_content_processed(self) -> bool:
        cursor = 0
        while True:
            res = await self.r.hscan(self.content_key, cursor, count=100)
            # logger.info(f"hscan {res=}")
            for __url_md5, raw_state in res[1].items():
                content_state = json.loads(raw_state.decode())
                content_state = ContentState(**content_state)
                if content_state.status == ContentStatus.DOWNLOAD_SUCCESS:
                    return False
            cursor = res[0]
            if cursor == 0:
                break
        return True

    async def inc_complete_urls(self):
        await self.r.hincrby(self.meta_key, "complete_urls", 1)
        await self.r.publish(self.stats_channel, "complete_urls")

    async def inc_failed_urls(self):
        await self.r.hincrby(self.meta_key, "failed_urls", 1)
        await self.r.publish(self.stats_channel, "failed_urls")

    async def inc_rejected_urls(self):
        await self.r.hincrby(self.meta_key, "rejected_urls", 1)
        await self.r.publish(self.stats_channel, "rejected_urls")

    async def inc_crawled_content(self):
        await self.r.hincrby(self.meta_key, "crawled_content", 1)
        await self.r.publish(self.stats_channel, "crawled_content")

    async def inc_evaluated_content(self):
        await self.r.hincrby(self.meta_key, "evaluated_content", 1)
        await self.r.publish(self.stats_channel, "evaluated_content")

    async def inc_failed_content(self):
        await self.r.hincrby(self.meta_key, "failed_content", 1)
        await self.r.publish(self.stats_channel, "failed_content")

    async def inc_tag_usage(self, tag_id: str, keepout: Optional[bool]):
        if not keepout:
            await self.r.hincrby(self.tags_usage_key, tag_id, 1)
        else:
            await self.r.hincrby(self.tags_usage_key, f"n/{tag_id}", 1)

    async def get_tag_usage(self, tag_id: str):
        tag_id = str(tag_id)
        bres = await self.r.hget(self.tags_usage_key, tag_id)
        usage = int(bres.decode()) if bres is not None else 0
        bres = await self.r.hget(self.tags_usage_key, f"n/{tag_id}")
        keepout = int(bres.decode()) if bres is not None else 0
        return (usage, keepout)

    async def exists(self):
        res = await self.r.exists(self.meta_key)
        return res

    async def set_last_reported_status(self, status: CrawlerHintURLStatus):
        await self.r.hset(self.meta_key, "last_reported_status", status.value)
        await self.r.publish(self.stats_channel, "status_change")

    async def get_last_reported_status(self) -> Optional[CrawlerHintURLStatus]:
        bres = await self.r.hget(self.meta_key, "last_reported_status")
        return CrawlerHintURLStatus(int(bres.decode())) if bres is not None else None

    async def inc_since_last_tagged(self):
        await self.r.hincrby(self.meta_key, "since_last_tagged", 1)

    async def reset_since_last_tagged(self):
        await self.r.hset(self.meta_key, "since_last_tagged", 0)

    async def get_since_last_tagged(self):
        bres = await self.r.hget(self.meta_key, "since_last_tagged")
        return int(bres.decode()) if bres is not None else 0

    # async def postpone(self):
    #     await self.set_status(SessionStatus.POSTPONED)
    #     await self.r.hset(self.meta_key, "last_postponed", int(time.time()))
    #     await self.r.hincrby(self.meta_key, "total_postponed", 1)
    #     await self.r.sadd(POSTPONED_SESSIONS_KEY, self.id)

    async def add_heartbeat(self, worker_id):
        await self.r.hset(self.heartbeat_key, worker_id, int(time.time()))

    async def get_heartbeat(self, worker_id):
        bres = await self.r.hget(self.heartbeat_key, worker_id)
        return int(bres.decode()) if bres is not None else 0


class SessionManager:
    def __init__(self, host, port=6379, db=0):
        self.r = Redis(host=host, port=port, db=db)

    async def stop(self):
        await self.r.connection_pool.aclose()
        del self.r

    async def is_ready(self) -> bool:
        try:
            await self.r.ping()
            return True
        except RedisConnectionError:
            return False

    async def create(self, hint_id=0, url: AnyUrl | str = "") -> Session:
        session_id = self.gen_session_id()
        await self.r.hset(
            SessionManager.get_meta_key(session_id),
            mapping={
                "version": SESSION_VERSION,
                "hint_id": hint_id,
                "url": str(url),
                "total_urls": 0,
                "complete_urls": 0,
                "failed_urls": 0,
                "rejected_urls": 0,
                "crawled_content": 0,
                "evaluated_content": 0,
                "failed_content": 0,
                "status": SessionStatus.NORMAL.value,
                "last_reported_status": CrawlerHintURLStatus.Unprocessed.value,
                # "last_postponed": 0,
                # "total_postponed": 0,
            },
        )

        # logger.info( f'hset result {r=} {type(r)=}')
        return Session(session_id, self.r)

    async def has(self, session_id) -> bool:
        res = await self.r.exists(SessionManager.get_meta_key(session_id))
        # logger.info( f'sessionmanager.has {res=} {type(res)=}')
        return res

    async def get(self, session_id) -> Optional[Session]:
        if await self.has(session_id):
            res = Session(session_id, self.r)
            if await res.is_valid():
                return res
        return None

    async def remove(self, session_id):
        await self.r.delete(SessionManager.get_meta_key(session_id))
        await self.r.delete(SessionManager.get_urls_key(session_id))
        await self.r.delete(SessionManager.get_content_key(session_id))
        await self.r.delete(SessionManager.get_tags_usage_key(session_id))
        await self.r.delete(SessionManager.get_heartbeat_key(session_id))

    def gen_session_id(self) -> str:
        # TODO: add existance check
        return md5(str(time.time()))

    @staticmethod
    def get_meta_key(session_id):
        return f"{SESSION_METADATA_KEY_PREFIX}{session_id}"

    @staticmethod
    def get_urls_key(session_id):
        return f"{SESSION_URLS_KEY_PREFIX}{session_id}"

    @staticmethod
    def get_content_key(session_id):
        return f"{SESSION_CONTENT_KEY_PREFIX}{session_id}"

    @staticmethod
    def get_tags_usage_key(session_id):
        return f"{SESSION_TAGS_USAGE_KEY_PREFIX}{session_id}"

    @staticmethod
    def get_heartbeat_key(session_id):
        return f"{SESSION_HEARTBEAT_KEY_PREFIX}{session_id}"

    async def get_ids(self, limit) -> List[str]:
        keys = await self.r.keys(f"{SESSION_METADATA_KEY_PREFIX}*")
        if len(keys) > limit:
            keys = keys[0:limit]
        n = len(SESSION_METADATA_KEY_PREFIX)
        return [k[n:].decode() for k in keys]

    # async def list_postponed(self, limit: Optional[int] = None):
    #     if limit is None:
    #         _set = await self.r.smembers(POSTPONED_SESSIONS_KEY)
    #     else:
    #         _set = await self.r.sscan(POSTPONED_SESSIONS_KEY, count=limit)
    #         _set = _set[1]
    #     if _set:
    #         return [session_id.decode() for session_id in _set]
    #     return []

    # async def pop_postponed(self, session_id):
    #     if not await self.r.sismember(POSTPONED_SESSIONS_KEY, session_id):
    #         return None
    #     await self.r.srem(POSTPONED_SESSIONS_KEY, session_id)
    #     return await self.get(session_id)

    # async def push_postponed(self, session_id):
    #     await self.r.sadd(POSTPONED_SESSIONS_KEY, session_id)
