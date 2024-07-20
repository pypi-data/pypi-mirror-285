import os

from abc import ABCMeta, abstractmethod

from typing import Any, List
from configparser import ConfigParser
from loguru import logger
from loguru._logger import Logger
from pathlib import Path

from .base_config import BaseConfig


class ConfigTemplate(metaclass=ABCMeta):
    __instance__: Any = None

    __parser: ConfigParser = ConfigParser()
    __base_config: BaseConfig = BaseConfig
    __log_app: Logger = logger

    TYPE: List[str] = ["BASE"]

    @classmethod
    def __new__(cls, *args, **kwargs):
        if cls.__instance__ is None:
            cls.__instance__ = object.__new__(cls)
        return cls.__instance__

    @classmethod
    def create_config(cls, base_path: str, config_url: str = "config/config.ini"):
        base_url: str = Path(base_path).parent.parent.parent.__str__()
        config_path: str = os.path.join(base_url, config_url)
        return cls(base_url, config_path)

    def __init__(self, base_url: str, config_path: str):
        self.__parser_init(config_path)
        self.config_init(base_url)
        self.__log_init()
        self.mysql_init()
        self.redis_init()
        self.hbase_init()
        self.kafka_init()

    def __parser_init(self, config_path: str) -> None:
        """初始化配置文件"""
        self.__parser.read(config_path, encoding="utf-8")

    def __log_init(self):
        log_url: str = self.config_object.base_config.log_url
        log_name: str = "log_{time:%Y%m%d%H}.log"
        log_path: str = os.path.join(log_url, log_name)
        self.__log_app.add(log_path, rotation="1 hours", retention="3 days", encoding="utf-8")

    def mysql_init(self) -> None:
        pass

    def redis_init(self) -> None:
        pass

    def kafka_init(self) -> None:
        pass

    def hbase_init(self) -> None:
        pass

    @abstractmethod
    def config_init(self, base_url: str) -> None:
        self.__base_config.load_path(base_url, **self.__parser[self.TYPE[0]])

    @property
    def config_object(self) -> BaseConfig:
        return self.__base_config

    @property
    def printf(self):
        return self.__log_app

    @property
    def parser(self) -> ConfigParser:
        return self.__parser
