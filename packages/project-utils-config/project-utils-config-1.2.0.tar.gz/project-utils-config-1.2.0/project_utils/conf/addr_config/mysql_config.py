from typing import Dict, Union

from .base_config import BaseConfig


class MysqlConfig(BaseConfig):
    user: str
    password: str
    database: str

    def __init__(self, host: str, user: str, password: str, database: str, port: str = "3306"):
        super().__init__(host=host, port=port)
        self.user = user
        self.password = password
        self.database = database

    def to_dict(self) -> Dict[str, Union[str, int]]:
        result: Dict[str, Union[str, int]] = super().to_dict()
        result.update({
            "user": self.user,
            "password": self.password,
            "database": self.database
        })
        return result
