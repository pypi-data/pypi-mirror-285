from abc import ABCMeta, abstractmethod

from ._context import MapContext


class BaseMapper(metaclass=ABCMeta):
    @abstractmethod
    async def map(self, key: str, value: str, context: MapContext):
        ...
