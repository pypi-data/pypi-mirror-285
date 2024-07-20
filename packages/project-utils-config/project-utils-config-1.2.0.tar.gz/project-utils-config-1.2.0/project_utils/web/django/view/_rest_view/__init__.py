from ._base_view import BaseRestAPIView
from ._async_base_view import AsyncBaseAPIView

BaseView = RestAPIView = RestView = BaseRestAPIView
AsyncBaseView = AsyncBaseAPIView

__all__ = [
    "BaseView",
    "RestAPIView",
    "RestView",
    "BaseRestAPIView",
    "AsyncBaseView",
    "AsyncBaseAPIView",
]
