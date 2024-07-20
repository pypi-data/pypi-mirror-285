import jwt
import json
import uuid
import base64
import traceback

from abc import ABCMeta

from typing import List, Optional, Dict, Any, Union

from django.conf import settings
from django.contrib.auth import authenticate

from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import ReturnDict

from project_utils.time import compute_day
from project_utils.exception import DjangoWebException, ViewException
from project_utils.web.django.conf import DjangoConfig
from project_utils.web.django.serializer import BaseSerializer
from project_utils.web.django.response import WebResponse

from .._async_view import AsyncAPIView

from ._model import BaseUserModel


class BaseUserLoginView(APIView, metaclass=ABCMeta):
    config: DjangoConfig
    model: BaseUserModel
    serializer: BaseSerializer

    require: List[str] = ["username", "password", "checkcode"]
    pop_field: List[str] = ["password", "last_login", "is_superuser", "first_name", "last_name", "is_staff",
                            "is_active", "date_joined", "is_delete", "groups", "user_permissions"]

    def check(self, params: Dict[str, Any], field_list: List[str]):
        for field in field_list:
            assert field in params and params.get(field) is not None, Exception(
                f"Field name's {field} is not in request field list or name's {field} value is null!")

    def show_exception(self, exception: DjangoWebException):
        self.config.printf.error(exception.error_detail)
        self.config.printf.warning(exception.error_summary)

    def create_exception(self, status, e: Exception):
        return ViewException(status, str(e), traceback.format_exc())

    def before_login(self, request: Request, params: Dict[str, Any]):
        username: str = params.get("username")
        password: str = params.get("password")
        checkcode: str = params.get("checkcode")
        usercode: Optional[str] = request.session.get("user_code")
        assert usercode, Exception("Session save user code value's null!")
        localcode: str = self.UserCode(username, password, usercode).encode()
        assert checkcode == localcode, Exception("Local save code and user input code not match!")
        return self.UserInfo(username, password)

    def logined(self, request: Request, serializer: BaseSerializer) -> str:
        data: ReturnDict = serializer.data.copy()
        exp: float = compute_day(7).timestamp()
        payload: Dict[str, Union[str, float]] = {"exp": exp, "user": json.dumps(data)}
        token: str = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
        request.session['usertoken'] = token
        return token

    def pop(self, data: ReturnDict, pop_field) -> ReturnDict:
        for field in pop_field:
            data.pop(field)
        return data

    def get(self, request: Request, id: Optional[str] = None) -> Response:
        self.config.printf.info(f"request success!\npath is {request.path}\nmethod is get\nselect id is {id}")
        user_code: str = uuid.uuid4().hex[:12]
        request.session["user_code"] = user_code
        self.config.printf.success(f"View success!\nPath is {request.path}\nMethod is {request.method}\nData is {user_code}")
        return WebResponse(data={"code": user_code}).to_rest_response()

    def post(self, request: Request) -> Response:
        self.config.printf.info(f"request success!\npath is {request.path}\nmethod is post")
        params: Dict[str, Any] = request.data
        try:
            self.check(params, self.require)
        except Exception as e:
            _e: DjangoWebException = self.create_exception(403, e)
            self.show_exception(_e)
            return WebResponse(status=403, error=_e).to_rest_response()
        try:
            user_info: BaseUserLoginView.UserInfo = self.before_login(request, params)
        except Exception as e:
            _e: DjangoWebException = self.create_exception(403, e)
            self.show_exception(_e)
            return WebResponse(status=403, error=_e).to_rest_response()
        user: Optional[BaseUserModel] = authenticate(**user_info.to_dict())
        try:
            assert user, Exception("Input username and password not match!")
        except Exception as e:
            _e: DjangoWebException = self.create_exception(403, e)
            self.show_exception(_e)
            return WebResponse(status=403, error=_e).to_rest_response()
        serializer: BaseSerializer = self.serializer(instance=user)
        try:
            token: str = self.logined(request, serializer)
        except Exception as e:
            _e: DjangoWebException = self.create_exception(410, e)
            self.show_exception(_e)
            return WebResponse(status=410, error=_e).to_rest_response()
        result: ReturnDict = self.pop(serializer.data.copy(), self.pop_field)
        self.config.printf.success(f"View success!\nPath is {request.path}\nMethod is {request.method}\nData is {token}")
        return WebResponse(data={"user_info": result, "user_token": token}).to_rest_response()

    class UserCode:
        username: str
        password: str
        checkcode: str

        def __init__(self, username: str, password: str, checkcode: str):
            self.username = username
            self.password = password
            self.checkcode = checkcode

        def encode(self) -> str:
            code: str = "_".join([self.username, self.checkcode, self.password])
            return base64.b64encode(code.encode("utf-8")).decode("utf-8")

    class UserInfo:
        username: str
        password: str

        def __init__(self, username: str, password: str):
            self.username = username
            self.password = password

        def to_dict(self):
            return {
                "username": self.username,
                "password": self.password
            }


class AsyncBaseUserLoginView(AsyncAPIView, metaclass=ABCMeta):
    config: DjangoConfig
    model: BaseUserModel
    serializer: BaseSerializer

    require: List[str] = ["username", "password", "checkcode"]
    pop_field: List[str] = ["password", "last_login", "is_superuser", "first_name", "last_name", "is_staff",
                            "is_active", "date_joined", "is_delete", "groups", "user_permissions"]

    async def check(self, params: Dict[str, Any], field_list: List[str]):
        for field in field_list:
            assert field in params and params.get(field) is not None, Exception(
                f"Field name's {field} is not in request field list or name's {field} value is null!")

    async def show_exception(self, exception: DjangoWebException):
        self.config.printf.error(exception.error_detail)
        self.config.printf.warning(exception.error_summary)

    async def create_exception(self, status: int, e: Exception):
        return ViewException(status, str(e), traceback.format_exc())

    async def before_login(self, request: Request, params: Dict[str, Any]):
        username: str = params.get("username")
        password: str = params.get("password")
        checkcode: str = params.get("checkcode")
        usercode: Optional[str] = request.session["user_code"]
        assert usercode, Exception("Session save user code value's null!")
        localcode: str = await self.UserCode(username, password, usercode).encode()
        assert checkcode == localcode, Exception("Local save code and user input code not match!")
        return self.UserInfo(username, password)

    async def logined(self, request: Request, serializer: BaseSerializer) -> str:
        data: ReturnDict = serializer.data.copy()
        exp: float = compute_day(7).timestamp()
        payload: Dict[str, Union[str, float]] = {"exp": exp, "user": json.dumps(data)}
        token: str = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
        request.session['usertoken'] = token
        return token

    async def pop(self, data: ReturnDict, pop_field) -> ReturnDict:
        for field in pop_field:
            data.pop(field)
        return data

    async def get(self, request: Request, id: Optional[str] = None) -> Response:
        self.config.printf.info(f"request success!\npath is {request.path}\nmethod is get\nselect id is {id}")
        user_code: str = uuid.uuid4().hex[:12]
        request.session["user_code"] = user_code
        self.config.printf.success(
            f"View success!\nPath is {request.path}\nMethod is {request.method}\nData is {user_code}")
        return WebResponse(data={"code": user_code}).to_rest_response()

    async def post(self, request: Request) -> Response:
        self.config.printf.info(f"request success!\npath is {request.path}\nmethod is post")
        params: Dict[str, Any] = request.data
        try:
            await self.check(params, self.require)
        except Exception as e:
            _e: DjangoWebException = await self.create_exception(403, e)
            await self.show_exception(_e)
            return WebResponse(status=403, error=_e).to_rest_response()
        try:
            user_info: AsyncBaseUserLoginView.UserInfo = await self.before_login(request, params)
        except Exception as e:
            _e: DjangoWebException = await self.create_exception(403, e)
            await self.show_exception(_e)
            return WebResponse(status=403, error=_e).to_rest_response()
        user: Optional[BaseUserModel] = authenticate(**await user_info.to_dict())
        try:
            assert user, Exception("Input username and password not match!")
        except Exception as e:
            _e: DjangoWebException = await self.create_exception(403, e)
            await self.show_exception(_e)
            return WebResponse(status=403, error=_e).to_rest_response()
        serializer: BaseSerializer = self.serializer(instance=user)
        try:
            token: str = await self.logined(request, serializer)
        except Exception as e:
            _e: DjangoWebException = await self.create_exception(410, e)
            await self.show_exception(_e)
            return WebResponse(status=410, error=_e).to_rest_response()
        result: ReturnDict = await self.pop(serializer.data.copy(), self.pop_field)
        self.config.printf.success(f"View success!\nPath is {request.path}\nMethod is {request.method}\nData is {token}")
        return WebResponse(data={"user_info": result, "user_token": token}).to_rest_response()

    class UserCode:
        username: str
        password: str
        checkcode: str

        def __init__(self, username: str, password: str, checkcode: str):
            self.username = username
            self.password = password
            self.checkcode = checkcode

        async def encode(self) -> str:
            code: str = "_".join([self.username, self.checkcode, self.password])
            return base64.b64encode(code.encode("utf-8")).decode("utf-8")

    class UserInfo:
        username: str
        password: str

        def __init__(self, username: str, password: str):
            self.username = username
            self.password = password

        async def to_dict(self):
            return {
                "username": self.username,
                "password": self.password
            }
