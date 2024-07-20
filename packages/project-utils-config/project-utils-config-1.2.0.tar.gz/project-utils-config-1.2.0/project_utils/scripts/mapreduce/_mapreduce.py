import os.path
import re
import uuid

from aiofiles import open
from datetime import datetime
from asyncio import Queue, gather
from typing import ClassVar, List, Dict
from project_utils.time import datetime_to_str

from .._base import BaseScript
from ._mapper import BaseMapper
from ._reducer import BaseReducer
from ._context import MapContext, ReduceContext


class BaseMapReduce(BaseScript):
    name: str = "mapreduce"
    input_path: str
    output_path: str

    map_class: ClassVar[BaseMapper]
    reduce_class: ClassVar[BaseReducer]

    __mapper: BaseMapper
    __reducer: BaseReducer

    __before_map: Queue
    __map: Queue
    __after_map: Queue

    __before_map_status: bool
    __map_status: bool
    __after_map_status: bool

    __before_reduce: Queue
    __reduce: Queue
    __after_reduce: Queue

    __before_reduce_status: bool
    __reduce_status: bool
    __after_reduce_status: bool

    __map_job: MapContext
    __reduce_job: ReduceContext

    __map_keys: List[str]
    __map_data: Dict[str, List[int]]
    __reduce_keys: List[str]
    __reduce_data: Dict[str, int]

    def __init__(self, size: int = 10000, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__mapper = self.map_class()
        self.__reducer = self.reduce_class()
        self.__before_map = Queue(size)
        self.__before_map_status = False
        self.__map = Queue(size)
        self.__map_status = False
        self.__after_map = Queue(size)
        self.__after_reduce_status = False
        self.__before_reduce = Queue(size)
        self.__before_reduce_status = False
        self.__reduce = Queue(size)
        self.__reduce_status = False
        self.__after_reduce = Queue(size)
        self.__after_reduce_status = False
        self.__map_job = MapContext(self.__map)
        self.__reduce_job = ReduceContext(self.__reduce)
        self.__map_keys = []
        self.__map_data = {}

    async def producer(self):
        async with open(self.input_path) as f:
            async for line in f:
                yield line.strip("\n")

    async def __before_map_task(self):
        async for item in self.producer():
            await self.__before_map.put(item)
        self.__before_map_status = True

    async def __map_task(self):
        while not self.__before_map_status and not self.__before_map.empty():
            data: str = await self.__before_map.get()
            key: str = uuid.uuid4().hex
            await self.__mapper.map(key, data, self.__map_job)
        self.__map_status = True

    async def __after_map_task(self):
        while not self.__map_status and not self.__map.empty():
            data: dict = await self.__map.get()
            key: str = data.get("key")
            if key not in self.__map_keys:
                self.__map_keys.append(key)
                self.__map_keys.sort()
            await self.__after_map.put(data)
        self.__after_map_status = True

    async def before_reduce_task(self):
        while True:
            if self.__after_map_status and self.__after_map.empty():
                self.__before_reduce_status = True
                return
            if not self.__after_map_status and self.__before_reduce.qsize() <= 100:
                data: dict = await self.__after_map.get()
                key: str = data.get("key")
                val: int = data.get("val")
                if key not in self.__map_data:
                    self.__map_data[key] = []
                self.__map_data[key].append(val)
            else:
                for key in self.__map_keys:
                    msg: dict = {"key": key, "values": self.__map_data[key]}
                    await self.__before_reduce.put(msg)
                self.__map_data.clear()
                self.__map_keys.clear()

    async def __reduce_task(self):
        while not self.__before_reduce_status and not self.__reduce.empty():
            data: dict = await self.__reduce.get()
            key: str = data.get("key")
            values: List[int] = data.get("values")
            await self.__reducer.reduce(key, values, self.__reduce_job)
        self.__reduce_status = True

    async def __after_reduce_task(self):
        while not self.__reduce_status and not self.__after_reduce.empty():
            data: dict = await self.__after_reduce.get()
            key: str = data.get("key")
            value: int = data.get("value")
            if key not in self.__reduce_keys:
                self.__reduce_keys.append(key)
                self.__reduce_data[key] = value
                self.__reduce_keys.sort()
            else:
                self.__reduce_data[key] += value
            if len(self.__reduce_keys) > 1000:
                pop_key: str = self.__reduce_keys.pop(0)
                if len(os.listdir(self.output_path)) == 0:
                    output_name: str = f"{self.name}_{datetime_to_str(datetime.now(), '%Y%m%d%H%M%S')}.txt"
                    output_path: str = os.path.join(self.output_path, output_name)
                    async with open(output_path, "a") as f:
                        line: str = f"{pop_key}\t{self.__reduce_data.get(pop_key)}\n"
                        await f.write(line)
        listdir: list = os.listdir(self.output_path)
        listdir.sort()
        output_name: str = listdir[-1]
        output_path = os.path.join(self.output_path, output_name)
        async with open(output_path, "r+") as f:
            for key in self.__reduce_keys:
                line: str = f"{key}\t{self.__reduce_data.get(key)}\n"
                await f.write(line)

    async def handler(self, *args, **kwargs):
        await gather(
            self.__before_map_task(),
            self.__map_task(),
            self.__after_map_task(),
            self.before_reduce_task(),
            self.__reduce_task(),
            self.__after_reduce_task()
        )
