from enum import Enum
from typing import Optional
from ..common.session_manager import Session


class YieldResult(Enum):
    NoResult = 0
    ContentDownloadSuccess = 1
    ContentDownloadFailure = 2
    ContentIgnored = 3


class WorkerContext:
    session: Optional[Session]
    yield_result: YieldResult

    def __init__(self, session: Optional[Session]):
        self.session = session
        self.yield_result = YieldResult.NoResult
