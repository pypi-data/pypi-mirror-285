import jwt
import json
import traceback

from abc import ABCMeta, abstractmethod
from typing import Optional

from project_utils.exception import ViewException

from ..conf import DjangoConfig
from ..request import WebRequest
from ._types import REQUEST_TYPE, PARAMS_TYPE, USER_TYPE


class Base(metaclass=ABCMeta):
    request: REQUEST_TYPE
    method: str
    config: DjangoConfig

    def __init__(self, request: REQUEST_TYPE, method: str, config: DjangoConfig):
        self.request = request
        self.method = method
        self.config = config

    @abstractmethod
    def parse_params(self) -> PARAMS_TYPE:
        pass

    def parse_token(self, request: WebRequest) -> USER_TYPE:
        for path in self.config.system_path:
            if path and path in request.path:
                return {}
        session_token: Optional[str] = request.session.get("usertoken")
        request_token: Optional[str] = request.meta.get("HTTP_AUTHORIZATION")
        assert session_token and request_token, ViewException("Input token value isn't null!", "token为空")
        assert session_token == request_token, ViewException("Input token value and session token isn't match!")
        token = session_token = request_token
        user_body: str = jwt.decode(token, key=self.config.settings.SECRET_KEY, algorithms="HS256")['user']
        return json.loads(user_body)

    def request_init(self, config: DjangoConfig) -> WebRequest:
        request: WebRequest = WebRequest(request=self.request, config=config)
        try:
            params: PARAMS_TYPE = self.parse_params()
        except Exception as e:
            raise ViewException(error_summary=str(e), error_detail=traceback.format_exc())

        request.params = params
        try:
            user: USER_TYPE = self.parse_token(request)
        except Exception as e:
            raise ViewException(error_summary=str(e), error_detail=traceback.format_exc())
        request.user = user
        return request

    async def async_request_init(self, config: DjangoConfig):
        return self.request_init(config)
