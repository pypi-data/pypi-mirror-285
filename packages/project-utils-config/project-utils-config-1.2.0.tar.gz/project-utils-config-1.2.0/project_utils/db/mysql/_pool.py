import traceback

from typing import Any, Optional

from pymysql import connect
from pymysql.connections import Connection
from pymysql.cursors import DictCursor
from dbutils.pooled_db import PooledDB
from dbutils.steady_db import SteadyDBConnection

from project_utils.exception import MysqlException

from ._collection import MysqlCollection
from ._result import MysqlResult


class MysqlPool(MysqlCollection):
    use_pool: bool
    connection: Connection
    pool: Optional[PooledDB] = None

    def __init__(
            self,
            creator: Any,
            use_pool: bool = True,
            max_connections: int = 10,
            min_cached: int = 5,
            max_cached: int = 10,
            max_shared: int = 10,
            *args, **kwargs):
        self.use_pool = use_pool
        super().__init__(max_connections=max_connections, min_cached=min_cached, max_cached=max_cached,
                         max_shared=max_shared)
        if self.use_pool:
            if self.pool is None:
                self.pool = PooledDB(
                    creator,
                    self.min_cached,
                    self.max_cached,
                    self.max_shared,
                    self.max_connections,
                    self.blocking,
                    setsession=self.set_session,
                    ping=self.ping,
                    *args, **kwargs
                )
        else:
            self.connection = connect(*args, **kwargs)

    @property
    def conn(self):
        if self.use_pool:
            return self.pool.connection()
        else:
            return self.connection

    def running(self, sql: str, data: Any = None, many: bool = False) -> MysqlResult:
        if self.use_pool:
            conn: SteadyDBConnection = self.pool.connection()
        else:
            conn: Connection = self.connection
        cursor: DictCursor = conn.cursor(DictCursor)
        result: MysqlResult = self.execute(conn, cursor, sql, data, many)
        if self.use_pool:
            conn.close()
        return result

    def add_task(self, conn: SteadyDBConnection, sql: str, data: Any = None, many: bool = False) -> MysqlResult:
        cursor: DictCursor = conn.cursor()
        result: MysqlResult = self.async_execute(cursor, sql, data, many)
        return result

    def commit(self, conn: SteadyDBConnection):
        try:
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise MysqlException(str(e), traceback.format_exc())
