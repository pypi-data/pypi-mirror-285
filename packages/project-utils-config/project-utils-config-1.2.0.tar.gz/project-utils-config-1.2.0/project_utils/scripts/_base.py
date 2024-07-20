import asyncio

from typing import Optional
from asyncio import AbstractEventLoop
from abc import ABCMeta, abstractmethod

from project_utils.conf import ConfigTemplate


class BaseScript(metaclass=ABCMeta):
    config: ConfigTemplate
    loop: AbstractEventLoop

    def __init__(self, config: ConfigTemplate, loop: AbstractEventLoop):
        self.config = config
        self.loop = loop

    def async_start(self, *args, **kwargs):
        self.loop.run_until_complete(self.handler(*args, **kwargs))

    @abstractmethod
    async def handler(self, *args, **kwargs):
        ...

    @classmethod
    def run(cls, config: ConfigTemplate, loop: Optional[AbstractEventLoop] = None, *args, **kwargs):
        if loop is None:
            loop = asyncio.get_event_loop()
        this: cls = cls(config, loop)
        return this.async_start(*args, **kwargs)

    @classmethod
    def get_instance(cls, config: ConfigTemplate, loop: Optional[AbstractEventLoop] = None):
        if loop is None:
            loop = asyncio.get_event_loop()
        return cls(config, loop)
