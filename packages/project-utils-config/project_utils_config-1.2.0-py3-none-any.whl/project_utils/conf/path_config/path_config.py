import os

from typing import Any, Optional


class PathConfig:
    __instance__: Any
    # 日志文件目录
    __log_url: str
    # 数据文件目录
    __data_url: Optional[str]
    # 输出文件目录
    __output_url: Optional[str]
    # 测试文件目录
    __test_url: Optional[str]
    # 临时文件目录
    __tmp_url: Optional[str]

    def __init__(self, base_url: str, log_url: str, data_url: Optional[str] = None, output_url: Optional[str] = None,
                 test_url: Optional[str] = None, tmp_url: Optional[str] = None, ):
        self.__log_url = os.path.join(base_url, log_url)
        if data_url: self.__data_url = os.path.join(base_url, data_url)
        if output_url: self.__output_url = os.path.join(base_url, output_url)
        if test_url: self.__test_url = os.path.join(base_url, test_url)
        if tmp_url: self.__tmp_url = os.path.join(base_url, tmp_url)

    @property
    def log_url(self):
        if not os.path.exists(self.__log_url):
            os.mkdir(self.__log_url)
        return self.__log_url

    @property
    def data_url(self):
        if not os.path.exists(self.__data_url):
            os.mkdir(self.__data_url)
        return self.__data_url

    @property
    def output_url(self):
        if not os.path.exists(self.__output_url):
            os.mkdir(self.__output_url)
        return self.__output_url

    @property
    def test_url(self):
        if not os.path.exists(self.__test_url):
            os.mkdir(self.__test_url)
        return self.__test_url

    @property
    def tmp_url(self):
        if not os.path.exists(self.__tmp_url):
            os.mkdir(self.__tmp_url)
        return self.__tmp_url