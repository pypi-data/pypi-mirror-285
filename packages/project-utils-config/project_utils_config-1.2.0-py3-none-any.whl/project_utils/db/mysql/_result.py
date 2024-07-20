from typing import Optional, Any, List, Dict

from project_utils.exception import MysqlException


class MysqlResult:
    __status: int
    __data: Optional[List[Dict[str, Any]]]
    __error: Optional[str]

    def __init__(self, status: int, data: List[Dict[str, Any]] = None, error: Optional[str] = None):
        assert -1 <= status <= 1, MysqlException("params status value range from -1 to 1!")
        self.__status = status
        self.__data = data
        self.__error = error

    @property
    def status(self) -> int:
        return self.__status

    @property
    def data(self) -> List[Dict[str, Any]]:
        assert self.status == 1, MysqlException("not get select result!")
        return self.__data

    @property
    def error(self) -> Optional[str]:
        return self.__error
