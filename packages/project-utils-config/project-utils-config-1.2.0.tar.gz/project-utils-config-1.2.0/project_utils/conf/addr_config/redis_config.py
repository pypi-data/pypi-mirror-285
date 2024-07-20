from typing import Dict, Union, List, Optional, Any

from project_utils.exception import ConfigException
from .base_config import BaseConfig


class RedisConfig(BaseConfig):
    password: str
    db: int
    start_up_nodes: List[Dict[str, str]]
    is_cluster: bool

    def __init__(self,
                 host: str = "127.0.0.1",
                 port: str = "6379",
                 password: Optional[str] = None,
                 db: Optional[str] = None,
                 is_cluster: bool = False
                 ):
        self.is_cluster = is_cluster
        if not self.is_cluster:
            # 不使用集群模式
            assert db.isdigit(), ConfigException("params db type required integer!")
            super().__init__(port, host)
            self.password = password
            self.db = int(db)
        else:
            host_: List[str] = host.split(";")
            port_: List[str] = port.split(";")
            self.start_up_nodes = [{"host": host_[i], "port": port_[i]} for i in range(len(host_))]
            self.password = password

    # 使用集群模式

    def to_dict(self) -> Dict[str, Union[str, int]]:
        if self.is_cluster:
            result: Dict[str, Any] = {
                "start_up_nodes": self.start_up_nodes,
                "password": self.password
            }
        else:
            result: Dict[str, Union[str, int]] = super().to_dict()
            result.update({
                "password": self.password,
                "db": self.db
            })
        return result

    def to_url(self, index: Optional[str] = None, path: Optional[str] = None, is_ssl: bool = False) -> str:
        return f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"
