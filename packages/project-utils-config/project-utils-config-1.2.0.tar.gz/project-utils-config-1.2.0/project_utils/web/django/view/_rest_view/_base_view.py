import traceback

from abc import ABCMeta
from typing import Optional, List, Dict, Any, Union, Tuple

from django.db.models import Q
from django.db.models.query import QuerySet

from rest_framework.serializers import ReturnDict, ReturnList

from drf_yasg.openapi import Schema, Parameter
from drf_yasg.utils import swagger_auto_schema

from project_utils.exception import ViewException, DjangoWebException, ModelException
from project_utils.web.django.conf import DjangoConfig
from project_utils.web.django.model import BaseModel
from project_utils.web.django.serializer import BaseSerializer
from project_utils.web.django.pagination import BasePagination
from project_utils.web.django.request import WebRequest
from project_utils.web.django.response import WebResponse

from .._types import PARAMS_TYPE
from .._rest_api.api import RestAPIView
from project_utils.web.django.view._swagger_base import SwaggerTypeBase


class BaseRestAPIView(RestAPIView, metaclass=ABCMeta):
    require:List[str]
    pop_field:List[str]
    config: DjangoConfig
    model: BaseModel
    serializer: BaseSerializer
    page_class: BasePagination

    # 删除标记，False表示逻辑删除，True表示物理删除
    is_delete: bool = False
    # 过滤连接条件
    filter_condition: str = "OR"
    # 过滤符号
    filter_symbol: str = "contains"

    page_instance: BasePagination
    is_page: bool = True

    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except ViewException as e:
            self.show_exception(e)
            return WebResponse(e.status, error=e).to_rest_response()
        except ModelException as e:
            self.show_exception(e)
            return WebResponse(404, error=e).to_rest_response()
        except Exception as e:
            exception: ViewException = self.create_exception(410, e)
            self.show_exception(exception)
            return WebResponse(exception.status, error=exception).to_rest_response()

    def create_exception(self, status: int, e: Exception) -> ViewException:
        return ViewException(status, str(e), traceback.format_exc())

    def show_exception(self, e: DjangoWebException):
        self.config.printf.error(e.error_detail)
        self.config.printf.warning(e.error_summary)

    def __get_filter_field(self, params: PARAMS_TYPE) -> Dict[str, Any]:
        field: List[str] = self.model.get_fields()
        params_keys: List[str] = list(params.keys())
        filter_field: List[str] = list(set(field) & set(params_keys))
        filter_mapper: Dict[str, Any] = {key: params.get(key)[0] for key in filter_field}
        return filter_mapper

    def __filter(self, params: PARAMS_TYPE) -> QuerySet[BaseModel]:
        filter_field: Dict[str, Any] = self.__get_filter_field(params)
        instance: QuerySet[BaseModel] = self.model.objects.filter(is_delete=0)
        q: Q = Q()
        q.connector = self.filter_symbol
        for key, val in filter_field.items():
            if key == "is_delete":
                q.children.append((key, val))
            else:
                q.children.append((f"{key}__{self.filter_symbol}", val))
        return instance.filter(q)

    def check(self, params: PARAMS_TYPE, require_fields: List[str]):
        for field in require_fields:
            assert field in params and params.get(field) is not None, ViewException(403,
                                                                                    f"Field name's {field} is not in request field list or name's {field} value is null!")

    def before_select(self, request: WebRequest, instance: Union[QuerySet[BaseModel], BaseModel], many: bool) -> \
            Union[QuerySet[BaseModel], BaseModel]:
        return instance

    def __before_select(self, request: WebRequest, params: PARAMS_TYPE, many: bool, select_id: Optional[str]) -> \
            Union[QuerySet[BaseModel], BaseModel]:
        if many:
            instance: QuerySet[BaseModel] = self.__filter(params)
        else:
            instance: BaseModel = self.model.get_one(id=select_id)
        try:
            instance: Union[QuerySet[BaseModel], BaseModel] = self.before_select(request, instance, many)
            if not many and instance.is_delete:
                raise Exception("not find!")
        except Exception as e:
            raise self.create_exception(400, e)
        if many and self.is_page:
            self.page_instance = self.page_class()
            instance: QuerySet[BaseModel] = self.page_instance.paginate_queryset(instance, request.request, view=self)
        return instance

    @swagger_auto_schema(auto_schema=None)
    def get(self, request: WebRequest, id: Optional[str] = None) -> WebResponse:
        self.config.printf.info(f"request success!\npath is {request.path}\nmethod is get\nselect id is {id}")
        params: PARAMS_TYPE = request.params
        many: bool = id is None
        instance: QuerySet[BaseModel] = self.__before_select(request, params, many, id)
        serializer: BaseSerializer = self.serializer(instance=instance, many=many)
        data: Union[ReturnDict, ReturnList] = serializer.data.copy()
        data = self.__selected(request, data, many)
        request.config.printf.success(f"View success!\nPath is {request.path}\nMethod is {request.method}")
        return WebResponse(data=data)

    def __selected(self, request: WebRequest, data: Union[ReturnList, ReturnDict], many: bool) -> Union[
        ReturnDict, ReturnList]:
        try:
            data: Union[ReturnList, ReturnDict] = self.selected(request, data, many)
        except Exception as e:
            raise self.create_exception(410, e)
        if many and self.is_page:
            data: Dict[str, Any] = self.page_instance.get_paginated_response(data)
        return data

    def selected(self, request: WebRequest, data: Union[ReturnDict, ReturnList], many: bool) -> Union[
        ReturnDict, ReturnList]:
        return data

    def before_create(self, request: WebRequest, params: Dict[str, Any]) -> Dict[str, Any]:
        return params

    def __before_create(self, request: WebRequest, params: PARAMS_TYPE) -> Dict[str, Any]:
        try:
            return self.before_create(request, params)
        except Exception as e:
            raise self.create_exception(400, e)

    @swagger_auto_schema(auto_schema=None)
    def post(self, request: WebRequest) -> WebResponse:
        self.config.printf.info(f"request success!\npath is {request.path}\nmethod is post")
        params: PARAMS_TYPE = request.params
        data: Dict[str, Any] = self.__before_create(request, params)
        serializer: BaseSerializer = self.serializer(data=data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            raise self.create_exception(401, e)
        serializer.save()
        result: ReturnDict = self.__created(request, params, serializer)
        request.config.printf.success(f"View success!\nPath is {request.path}\nMethod is {request.method}")
        return WebResponse(data=result)

    def __created(self, request: WebRequest, params: PARAMS_TYPE, serializer: BaseSerializer) -> ReturnDict:
        try:
            return self.created(request, params, serializer.data.copy())
        except Exception as e:
            raise self.create_exception(410, e)

    def created(self, request: WebRequest, params: Dict[str, Any], data: ReturnDict) -> ReturnDict:
        return data

    def before_update(self, request: WebRequest, params: Dict[str, Any], instance: BaseModel) -> Tuple[
        Dict[str, Any], BaseModel]:
        return params, instance

    def __before_update(self, request: WebRequest, params: PARAMS_TYPE, instance: BaseModel) -> Tuple[
        Dict[str, Any], BaseModel]:
        try:
            return self.before_update(request, params, instance)
        except Exception as e:
            raise self.create_exception(400, e)

    @swagger_auto_schema(auto_schema=None)
    def put(self, request: WebRequest, id: Optional[str] = None) -> WebResponse:
        self.config.printf.info(f"request success!\npath is {request.path}\nmethod is put\nupdate id is {id}")
        assert id, ViewException(404, "update id value isn't null!")
        try:
            instance: BaseModel = self.model.get_one(id=id)
        except ModelException as e:
            raise self.create_exception(404, e)
        params: PARAMS_TYPE = request.params
        try:
            params, instance = self.__before_update(request, params, instance)
        except ViewException as e:
            self.show_exception(e)
            return WebResponse(status=401, error=e)
        serializer: BaseSerializer = self.serializer(instance=instance, data=params)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            _e: ViewException = self.create_exception(e)
            self.show_exception(_e)
            return WebResponse(status=402, error=_e)
        serializer.save()
        try:
            result: ReturnDict = self.__updated(request, serializer, params)
        except ViewException as e:
            self.show_exception(e)
            return WebResponse(status=410, error=e)
        request.config.printf.success(f"View success!\nPath is {request.path}\nMethod is {request.method}")
        return WebResponse(data=result)

    def __updated(self, request: WebRequest, serializer: BaseSerializer, params: PARAMS_TYPE) -> ReturnDict:
        try:
            return self.updated(request, serializer.data.copy(), params)
        except Exception as e:
            raise self.create_exception(410, e)

    def updated(self, request: WebRequest, data: ReturnDict, params: Dict[str, Any]) -> ReturnDict:
        return data

    def before_delete(self, request: WebRequest, params: Dict[str, Any], many: bool,
                      instance: Optional[BaseModel] = None) -> Union[QuerySet[BaseModel], BaseModel]:
        return instance

    def __before_delete(self, request: WebRequest, params: PARAMS_TYPE, many: bool,
                        delete_id: Optional[str] = None) -> Union[QuerySet[BaseModel], BaseModel]:
        instance: Optional[BaseModel] = None
        if not many:
            try:
                instance = self.model.get_one(id=delete_id)
            except ModelException as e:
                raise self.create_exception(404, e)
        try:
            return self.before_delete(request, params, many, instance)
        except Exception as e:
            raise self.create_exception(400, e)

    @swagger_auto_schema(auto_schema=None)
    def delete(self, request: WebRequest, id: Optional[str] = None) -> WebResponse:
        self.config.printf.info(f"request success!\npath is {request.path}\nmethod is delete\ndelete id is {id}")
        many: bool = id is None
        params: PARAMS_TYPE = request.params
        delete: Union[QuerySet[BaseModel], BaseModel] = self.__before_delete(request, params, many, id)
        serializer: BaseSerializer = self.serializer(instance=delete, many=many)
        data: Union[ReturnList, ReturnDict] = serializer.data.copy()
        delete_count: int = 0
        if many:
            for delete_item in delete:
                delete_count += 1
                if self.is_delete:
                    delete_item.delete()
                else:
                    delete_item.is_delete = True
                    delete_item.save()
        else:
            delete_count += 1
            if self.is_delete:
                delete.delete()
            else:
                delete.is_delete = True
                delete.save()
        self.__deleted(request, params, data)
        request.config.printf.success(f"View success!\nPath is {request.path}\nMethod is {request.method}")
        return WebResponse(data={"delete_count": delete_count})

    def __deleted(self, request: WebRequest, params: PARAMS_TYPE, data: Union[ReturnList, ReturnDict]):
        try:
            self.deleted(request, params, data)
        except Exception as e:
            raise self.create_exception(410, e)

    def deleted(self, request: WebRequest, params: Dict[str, Any], data: Union[ReturnList, ReturnDict]):
        pass

    def pop(self, data: ReturnDict, pop_field: Optional[List[str]] = None) -> ReturnDict:
        for field in pop_field:
            data.pop(field)
        return data
