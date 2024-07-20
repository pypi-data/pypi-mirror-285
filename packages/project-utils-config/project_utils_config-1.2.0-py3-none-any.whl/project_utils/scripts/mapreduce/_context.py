from asyncio import Queue
from typing import Optional
from abc import ABCMeta, abstractmethod


class BaseContext(metaclass=ABCMeta):
    queue: Queue

    def __init__(self, queue: Queue):
        self.queue = queue

    @abstractmethod
    async def write(self, key: str, val: Optional[int] = None):
        ...


class MapContext(BaseContext):
    async def write(self, key: str, val: Optional[int] = None):
        if val is None:
            val = 0
        msg: dict = {"key": key, "value": val}
        await self.queue.put(msg)


class ReduceContext(BaseContext):
    async def write(self, key: str, val: Optional[int] = None):
        msg: dict = {"key": key, "value": val}
        await self.qu
