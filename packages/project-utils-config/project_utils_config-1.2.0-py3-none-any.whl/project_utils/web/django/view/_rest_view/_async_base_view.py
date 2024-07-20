import traceback

from abc import ABCMeta
from typing import Optional, Dict, Any, Union, Tuple, List

from django.db.models.query import QuerySet, Q

from rest_framework.serializers import ReturnDict, ReturnList

from drf_yasg.openapi import Schema, Parameter
from drf_yasg.utils import swagger_auto_schema

from project_utils.exception import ViewException, ModelException
from project_utils.web.django.utils import DjangoUtils
from project_utils.web.django.conf import DjangoConfig
from project_utils.web.django.model import BaseModel
from project_utils.web.django.serializer import BaseSerializer
from project_utils.web.django.pagination import BasePagination
from project_utils.web.django.request import WebRequest
from project_utils.web.django.response import WebResponse

from .._rest_api import AsyncRestApi
from .._types import PARAMS_TYPE

from project_utils.web.django.view._swagger_base import SwaggerTypeBase


class AsyncBaseAPIView(AsyncRestApi, metaclass=ABCMeta):
    require: List[str]
    pop_field: List[str]
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

    async def dispatch(self, request, *args, **kwargs):
        try:
            return await super().dispatch(request, *args, **kwargs)
        except ViewException as e:
            await self.show_exception(e)
            response = WebResponse(e.status, error=e)
            self.response = self.finalize_response(request, response, *args, **kwargs)
            return self.response
        except Exception as e:
            exception: ViewException = await self.create_exception(410, e)
            await self.show_exception(exception)
            response = WebResponse(exception.status, error=exception)
            self.response = self.finalize_response(request, response, *args, **kwargs)
            return self.response

    async def __get_filter_field(self, params: PARAMS_TYPE) -> Dict[str, Any]:
        field: List[str] = await self.model.async_get_field()
        params_keys: List[str] = list(params.keys())
        filter_field: List[str] = list(set(field) & set(params_keys))
        filter_mapper: Dict[str, Any] = {key: params.get(key)[0] for key in filter_field}
        return filter_mapper

    async def create_exception(self, status: int, e: Exception) -> ViewException:
        return ViewException(status, str(e), traceback.format_exc())

    async def __filter(self, params: PARAMS_TYPE) -> QuerySet[BaseModel]:
        filter_field: Dict[str, Any] = await self.__get_filter_field(params)
        instance: QuerySet[BaseModel] = await self.model.async_filter(is_delete=0)
        q: Q = Q()
        q.connector = self.filter_symbol
        for key, val in filter_field.items():
            if key == "is_delete":
                q.children.append((key, val))
            else:
                q.children.append((f"{key}__{self.filter_symbol}", val))
        return await DjangoUtils.to_async_fun(instance.filter, q)

    async def before_select(self, request: WebRequest, instance: Union[QuerySet[BaseModel], BaseModel], many: bool) -> \
            Union[QuerySet[BaseModel], BaseModel]:
        return instance

    async def __before_select(self, request: WebRequest, params: PARAMS_TYPE, many: bool, select_id: Optional[str]) -> \
            Union[QuerySet[BaseModel], BaseModel]:
        if many:
            instance: QuerySet[BaseModel] = await self.__filter(params)
        else:
            instance: BaseModel = await self.model.async_get_one(id=select_id)
            if instance.is_delete:
                raise Exception("not find!")
        try:
            instance: Union[QuerySet[BaseModel], BaseModel] = await self.before_select(request, instance, many)
        except Exception as e:
            raise await self.create_exception(status=400, e=e)
        if many and self.is_page:
            self.page_instance = self.page_class()
            instance = await self.page_instance.async_paginate_queryset(instance, request.request, self)
        return instance

    @swagger_auto_schema(auto_schema=None)
    async def get(self, request: WebRequest, id: Optional[str] = None) -> WebResponse:
        self.config.printf.info(f"request success!\npath is {request.path}\nmethod is get\nselect id is {id}")
        params: PARAMS_TYPE = request.params
        many: bool = id is None
        instance: Union[QuerySet[BaseModel], BaseModel] = await self.__before_select(request, params, many, id)
        serializer: BaseSerializer = self.serializer(instance=instance, many=many)
        data: Union[ReturnList, ReturnDict] = serializer.data.copy()
        result: Union[ReturnList, ReturnDict] = await self.__selected(request, data, many)
        request.config.printf.success(f"View success!\nPath is {request.path}\nMethod is {request.method}")
        return WebResponse(data=result)

    async def __selected(self, request: WebRequest, data: Union[ReturnList, ReturnDict], many: bool) -> Union[
        ReturnDict, ReturnList]:
        try:
            data: Union[ReturnList, ReturnDict] = await self.selected(request, data, many)
        except Exception as e:
            raise await self.create_exception(410, e)
        if many and self.is_page:
            data: Dict[str, Any] = await self.page_instance.get_paginated_data(data)
        return data

    async def selected(self, request: WebRequest, data: Union[ReturnDict, ReturnList], many: bool) -> Union[
        ReturnDict, ReturnList]:
        return data

    async def before_create(self, request: WebRequest, params: Dict[str, Any]) -> Dict[str, Any]:
        return params

    async def __before_create(self, request: WebRequest, params: PARAMS_TYPE) -> Dict[str, Any]:
        try:
            return await self.before_create(request, params)
        except Exception as e:
            raise await self.create_exception(400, e)

    @swagger_auto_schema(auto_schema=None)
    async def post(self, request: WebRequest) -> WebResponse:
        self.config.printf.info(f"request success!\npath is {request.path}\nmethod is post")
        params: PARAMS_TYPE = request.params
        data: Dict[str, Any] = await self.__before_create(request, params)
        serializer: BaseSerializer = self.serializer(data=data)
        try:
            await DjangoUtils.to_async_fun(serializer.is_valid, raise_exception=True)
        except Exception as e:
            raise await self.create_exception(401, e)
        await serializer.async_save()
        result: ReturnDict = await self.__created(request, params, serializer)
        request.config.printf.success(f"View success!\nPath is {request.path}\nMethod is {request.method}")
        return WebResponse(data=result)

    async def __created(self, request: WebRequest, params: PARAMS_TYPE, serializer: BaseSerializer) -> ReturnDict:
        try:
            return await self.created(request, params, serializer.data.copy())
        except Exception as e:
            raise await self.create_exception(410, e)

    async def created(self, request: WebRequest, params: Dict[str, Any], data: ReturnDict) -> ReturnDict:
        return data

    async def before_update(self, request: WebRequest, params: Dict[str, Any], instance: BaseModel) -> Tuple[
        Dict[str, Any], BaseModel]:
        return params, instance

    async def __before_update(self, request: WebRequest, params: PARAMS_TYPE, instance: BaseModel) -> Tuple[
        Dict[str, Any], BaseModel]:
        try:
            return await self.before_update(request, params, instance)
        except Exception as e:
            raise await self.create_exception(400, e)

    @swagger_auto_schema(auto_schema=None)
    async def put(self, request: WebRequest, id: Optional[str] = None):
        self.config.printf.info(f"request success!\npath is {request.path}\nmethod is put\nupdate id is {id}")
        assert id, ViewException(error_summary="update id value isn't null!")
        try:
            instance: BaseModel = await self.model.async_get_one(id=id)
        except ModelException as e:
            raise await self.create_exception(404, e)
        params: PARAMS_TYPE = request.params
        params, instance = await self.__before_update(request, params, instance)
        serializer: BaseSerializer = self.serializer(instance=instance, data=params)
        try:
            await DjangoUtils.to_async_fun(serializer.is_valid, raise_exception=True)
        except Exception as e:
            raise await self.create_exception(403, e)
        await serializer.async_save()
        result: ReturnDict = await self.__updated(request, serializer, params)
        request.config.printf.success(f"View success!\nPath is {request.path}\nMethod is {request.method}")
        return WebResponse(data=result)

    async def __updated(self, request: WebRequest, serializer: BaseSerializer, params: PARAMS_TYPE) -> ReturnDict:
        try:
            return await self.updated(request, serializer.data.copy(), params)
        except Exception as e:
            raise await self.create_exception(410, e)

    async def updated(self, request: WebRequest, data: ReturnDict, params: Dict[str, Any]) -> ReturnDict:
        return data

    async def before_delete(self, request: WebRequest, params: Dict[str, Any], many: bool,
                            instance: Optional[BaseModel] = None) -> Union[QuerySet[BaseModel], BaseModel]:
        return instance

    async def __before_delete(self, request: WebRequest, params: PARAMS_TYPE, many: bool,
                              delete_id: Optional[str] = None) -> Union[QuerySet[BaseModel], BaseModel]:
        instance: Optional[BaseModel] = None
        if not many:
            try:
                instance: BaseModel = await self.model.async_get_one(id=delete_id)
            except ModelException as e:
                raise e

        try:
            return await self.before_delete(request, params, many, instance)
        except Exception as e:
            raise await self.create_exception(400, e)

    @swagger_auto_schema(auto_schema=None)
    async def delete(self, request: WebRequest, id: Optional[str] = None):
        self.config.printf.info(f"request success!\npath is {request.path}\nmethod is delete\ndelete id is {id}")
        params: PARAMS_TYPE = request.params
        many: bool = id is None
        instance: Union[QuerySet[BaseModel], BaseModel] = await self.__before_delete(request, params, many,
                                                                                     delete_id=id)
        serializer: BaseSerializer = self.serializer(instance=instance, many=many)
        data: Union[ReturnList, ReturnDict] = serializer.data.copy()
        delete_count: int = 0
        if many:
            for item in instance:
                delete_count += 1
                if self.is_delete:
                    await item.adelete()
                else:
                    item.is_delete = True
                    await item.asave()
        else:
            delete_count += 1
            if self.is_delete:
                await instance.adelete()
            else:
                instance.is_delete = True
                await instance.asave()
        await self.__deleted(request, params, data)
        request.config.printf.success(f"View success!\nPath is {request.path}\nMethod is {request.method}")
        return WebResponse(data={"delete_count": delete_count})

    async def __deleted(self, request: WebRequest, params: PARAMS_TYPE, data: Union[ReturnList, ReturnDict]):
        try:
            await self.deleted(request, params, data)
        except Exception as e:
            raise await self.create_exception(410, e)

    async def deleted(self, request: WebRequest, params: Dict[str, Any], data: Union[ReturnList, ReturnDict]):
        pass

    async def check(self, params: Dict[str, Any], field_list: List[str]):
        for field in field_list:
            assert field in params and params.get(field) is not None, ViewException(403,
                                                                                    f"Field name's {field} is not in request field list or name's {field} value is null!")

    async def pop(self, data: ReturnDict, pop_field: List[str]) -> ReturnDict:
        for field in pop_field:
            data.pop(field)
        return data
