import asyncio

from abc import ABCMeta, abstractmethod

from typing import Optional, Callable

from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.utils.deprecation import MiddlewareMixin

from project_utils.web.django.conf import DjangoConfig


class BaseMiddleware(MiddlewareMixin, metaclass=ABCMeta):
    config: DjangoConfig

    @abstractmethod
    def process_request(self, request: HttpRequest) -> Optional[HttpResponse]:
        return

    def process_view(self, request: HttpRequest, callback: Callable, callback_args: ..., callback_kwargs: ...) -> \
            Optional[HttpResponse]:
        return callback(request, *callback_args, **callback_kwargs)

    @abstractmethod
    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        return response

    @abstractmethod
    def process_exception(self, request: HttpRequest, exception: Exception) -> HttpResponse:
        return HttpResponse(str(exception))

    @abstractmethod
    def process_template_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        return response
