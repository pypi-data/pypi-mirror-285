import traceback

from abc import ABCMeta, abstractmethod
from typing import Optional

from rest_framework.views import APIView
from rest_framework.request import Request

from project_utils.exception import ViewException, DjangoWebException
from project_utils.web.django.conf import DjangoConfig
from project_utils.web.django import WebRequest, WebResponse

from .api_utils import BaseRestAPI


class RestAPIView(APIView, metaclass=ABCMeta):
    config: DjangoConfig

    def initialize_request(self, request, *args, **kwargs):
        request: Request = super().initialize_request(request, *args, **kwargs)
        api_util: BaseRestAPI = BaseRestAPI(request, method=request.method, config=self.config)
        web_request: WebRequest = api_util.request_init(self.config)
        return web_request

    def show_exception(self, e: DjangoWebException):
        self.config.printf.error(e.error_detail)
        self.config.printf.warning(e.error_summary)

    def create_exception(self, status: int, e: Exception) -> ViewException:
        return ViewException(status=status, error_summary=str(e), error_detail=traceback.format_exc())

    def initial(self, request, *args, **kwargs):
        self.request = request.request
        return super().initial(request.request)

    def finalize_response(self, request, response, *args, **kwargs):
        request: WebRequest = request
        response: WebResponse = response
        return super().finalize_response(request, response.to_rest_response())

    @abstractmethod
    def get(self, request: WebRequest, id: Optional[str] = None) -> WebResponse:
        ...

    @abstractmethod
    def post(self, request: WebRequest) -> WebResponse:
        ...

    @abstractmethod
    def put(self, request: WebRequest, id: Optional[str]) -> WebResponse:
        ...

    @abstractmethod
    def delete(self, request: WebRequest, id: Optional[str]) -> WebResponse:
        ...
