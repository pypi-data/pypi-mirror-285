import asyncio
import os
import io
from typing import Union
from contextlib import AbstractContextManager

from ..logger import logger
from .base_storage import BaseStorage


ONE_MB = 1024 * 1024


class FileStorageContextManager(AbstractContextManager):
    f: io.IOBase

    def __init__(self, path, mode):
        logger.info(f"Opening storage file: {path}, size={os.path.getsize(path)}")
        self.f = open(path, mode)

    def __enter__(self):
        return self.f

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.f.close()


class FileStorage(BaseStorage):
    def __init__(self, dst_path, must_exist=False):
        if must_exist is False:
            os.makedirs(dst_path, exist_ok=True)
        else:
            if not os.path.exists(dst_path):
                raise FileNotFoundError()
        self.dst_path = dst_path

    async def put(self, storage_id, content: Union[str, bytes, io.IOBase]):
        path = self.get_path(storage_id)
        logger.info(f"FileStorage::put {path=}")
        with open(path, "wb") as f:
            if isinstance(content, str):
                content = content.encode()
            if isinstance(content, bytes):
                f.write(content)
            elif isinstance(content, io.IOBase):
                content.seek(0, 0)
                total = 0
                while True:
                    buffer = content.read(ONE_MB)
                    if not buffer:
                        break
                    f.write(buffer)
                    total += len(buffer)
                    await asyncio.sleep(0)
                logger.info(f"put {total=}")
            else:
                raise Exception(f"Unknown source {type(content)=}")

    async def read(self, storage_id):
        # TODO: make async generator and read by chunks
        with open(self.get_path(storage_id), "rb") as f:
            res = f.read()
            return res

    def get_reader(self, storage_id) -> FileStorageContextManager:
        return FileStorageContextManager(self.get_path(storage_id), "rb")

    async def remove(self, storage_id):
        path = self.get_path(storage_id)
        logger.info(f"unlink {path=}")
        os.unlink(path)

    async def has(self, storage_id):
        path = self.get_path(storage_id)
        return os.path.exists(path)

    def get_path(self, storage_id):
        return os.path.join(self.dst_path, storage_id)
