from typing import Union, Dict, Any, Callable

from django.http.request import HttpRequest
from django.http.response import HttpResponse
from rest_framework.request import Request
from rest_framework.response import Response

from ..request import WebRequest
from ..response import WebResponse

REQUEST_TYPE = Union[HttpRequest, Request, WebRequest]
PARAMS_TYPE = Dict[str, Any]
USER_TYPE = Dict[str, str]
VIEW_TYPE = Callable[[Union[REQUEST_TYPE], Any, Any], Union[Response, WebResponse]]
API_VIEW_HANDLER_TYPE = Callable[[HttpRequest, Any, Any], HttpResponse]
BASE_API_TYPE = Callable[[VIEW_TYPE], API_VIEW_HANDLER_TYPE]
REST_VIEW_HANDLER_TYPE = Callable[[Request, Any, Any], Response]
REST_API_TYPE = Callable[[VIEW_TYPE], REST_VIEW_HANDLER_TYPE]
