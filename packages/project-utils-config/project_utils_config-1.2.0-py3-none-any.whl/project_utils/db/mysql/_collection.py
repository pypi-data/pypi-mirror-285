import traceback

from abc import ABCMeta

from typing import Any, Optional, List
from pymysql.cursors import DictCursor
from dbutils.steady_db import SteadyDBConnection

from ._result import MysqlResult
from ._types import RES_TYPE


class MysqlCollection(metaclass=ABCMeta):
    creator: Any
    max_connections: Optional[int]
    min_cached: Optional[int]
    max_cached: Optional[int]
    max_shared: Optional[int]
    blocking: bool
    set_session: List
    ping: int
    charset: str

    def __init__(
            self,
            max_connections: Optional[int] = None,
            min_cached: Optional[int] = None,
            max_cached: Optional[int] = None,
            max_shared: Optional[int] = None,
            blocking: bool = False,
            set_session: Optional[List] = None,
            ping: int = 0,
            charset: str = "utf8"
    ):
        """
        :param creator: 链接数据库的模块
        :param max_connections: 连接池允许的最大连接数，0和None表示不限制连接数
        :param min_cached: 初始化时，链接池中至少创建的空闲的链接，0表示不创建
        :param max_cached: 链接池中最多闲置的链接，0和None不限制
        :param max_shared: 一个链接最多被重复使用的次数，None表示无限制
        :param blocking: 连接池中如果没有可用连接后，是否阻塞等待。True，等待；False，不等待然后报错
        :param set_session: 开始会话前执行的命令列表。
        :param ping: ping MySQL服务端，检查是否服务可用。
            - 0 = None = never
            - 1 = default = whenever it is requested
            - 2 = when a cursor is created
            - 4 = when a query is executed
            - 7 = always
        :param charset:数据库编码
        """
        if set_session is None: self.set_session = []
        self.max_connections = max_connections
        self.min_cached = min_cached
        self.max_cached = max_cached
        self.max_shared = max_shared
        self.blocking = blocking
        self.ping = ping
        self.charset = charset

    def execute(self, conn: SteadyDBConnection, cursor: DictCursor, sql: str, data: Any = None,
                many: bool = False) -> MysqlResult:
        try:
            if not many:
                cursor.execute(sql, data)
            else:
                cursor.executemany(sql, data)
            res: RES_TYPE = cursor.fetchall()
            conn.commit()
            if len(res) == 0:
                return MysqlResult(0)
            else:
                return MysqlResult(1, data=res)
        except Exception as e:
            # traceback.print_exc()
            print(str(e))
            return MysqlResult(-1, error=str(e))
        finally:
            cursor.close()

    def async_execute(self, cursor: DictCursor, sql: str, data: Any = None, many: bool = False):
        try:
            if many:
                cursor.executemany(sql, data)
            else:
                cursor.execute(sql, data)
            res: RES_TYPE = cursor.fetchall()
            if len(res) == 0:
                return MysqlResult(0)
            else:
                return MysqlResult(1, data=res)
        except Exception as e:
            # traceback.print_exc()
            print(str(e))
            return MysqlResult(-1, error=str(e))
        finally:
            cursor.close()
