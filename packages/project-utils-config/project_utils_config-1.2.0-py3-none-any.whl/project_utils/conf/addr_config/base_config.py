from abc import ABCMeta
from typing import Any, Optional

from project_utils.exception import ConfigException


class BaseConfig(metaclass=ABCMeta):
    __instance__: Any = None
    host: str
    port: int

    def __new__(cls, *args, **kwargs):
        if cls.__instance__ is None:
            cls.__instance__ = object.__new__(cls)
        return cls.__instance__

    def __init__(self, port: str, host: str = "0.0.0.0"):
        assert port.isdigit(), ConfigException("params port type required integer!")
        self.host = host
        self.port = int(port)

    def to_dict(self) -> dict:
        return {
            "host": self.host,
            "port": self.port
        }

    def to_url(self, index: Optional[str] = None, path: Optional[str] = None, is_ssl: bool = False) -> str:
        result: list = []
        if self.port == 80 or self.port == 443:
            result.append("http" if self.port == 80 else "https")
        elif is_ssl:
            result.append("https")
        else:
            result.append("http")
        result.append(self.host)
        base_url: str = f"{result[0]}://{result[1]}"
        if self.port != 80 and self.port != 443:
            base_url += f":{self.port}"
        if index:
            base_url += f"/{index}"
        if path:
            if path.startswith("/"):
                base_url += path
            else:
                base_url += f"/{path}"
        return base_url
