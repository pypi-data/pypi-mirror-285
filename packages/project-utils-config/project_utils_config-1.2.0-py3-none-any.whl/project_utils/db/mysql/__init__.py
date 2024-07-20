from ._pool import MysqlPool
from ._result import MysqlResult

mysql_pool = pool = MysqlPool
mysql_result = result = MysqlResult

__all__ = [
    "mysql_pool",
    "pool",
    "MysqlPool",
    "mysql_result",
    "result",
    "MysqlResult"
]
