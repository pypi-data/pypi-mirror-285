from typing import Union, Dict, Any, Optional

from django.http.request import HttpRequest
from django.contrib.sessions.backends.db import SessionStore

from rest_framework.request import Request

from project_utils.web.django import DjangoConfig


class WebRequest:
    _config: DjangoConfig
    _request: Union[HttpRequest, Request]
    _user: Optional[Dict[str, str]]
    _params: Optional[Dict[str, Any]]

    def __init__(self, request: Union[HttpRequest, Request], config: DjangoConfig):
        self._request = request
        self._config = config

    @property
    def user(self) -> Dict[str, str]:
        return self._user

    @user.setter
    def user(self, value: Dict[str, str]):
        self._user = value

    @property
    def params(self):
        return self._params

    @params.setter
    def params(self, value):
        self._params = value

    @property
    def session(self) -> SessionStore:
        return self._request.session

    @property
    def path(self) -> str:
        return self._request.path

    @property
    def meta(self) -> Dict[str, str]:
        return self._request.META

    @property
    def request(self) -> Union[Request, HttpRequest]:
        return self._request

    @property
    def config(self) -> DjangoConfig:
        return self._config

    @property
    def method(self) -> str:
        return self._request.method
