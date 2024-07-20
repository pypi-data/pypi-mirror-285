from typing import Callable, Any, Dict, List
from asgiref.sync import sync_to_async

from project_utils.exception import ViewException


class DjangoUtils:
    @staticmethod
    async def to_async_fun(fun: Callable, *args, **kwargs) -> Any:
        return await sync_to_async(fun)(*args, **kwargs)

    @staticmethod
    async def check(params: Dict[str, Any], field_list: List[str]):
        for field in field_list:
            assert field in params and params.get(field) is not None, ViewException(403,
                                                                                    f"Field name's {field} is not in request field list or name's {field} value is null!")
