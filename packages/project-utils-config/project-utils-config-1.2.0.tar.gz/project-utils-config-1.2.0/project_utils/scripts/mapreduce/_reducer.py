from typing import List
from abc import ABCMeta, abstractmethod

from ._context import ReduceContext


class BaseReducer(metaclass=ABCMeta):
    @abstractmethod
    async def reduce(self, key: str, values: List[int], context: ReduceContext):
        ...
