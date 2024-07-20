from .api import RestAPIView
from .async_api import AsyncRestApi

rest_api = rest_api_view = RestAPIView
async_rest_api = async_rest_api_view = AsyncRestApi

__all__ = [
    "rest_api",
    "rest_api_view",
    "RestAPIView",
    "async_rest_api_view",
    "async_rest_api",
    "AsyncRestApi"
]
