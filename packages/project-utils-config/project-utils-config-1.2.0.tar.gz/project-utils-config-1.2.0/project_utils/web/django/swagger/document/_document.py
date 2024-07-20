from abc import ABCMeta, abstractmethod
from typing import List, Dict

from project_utils.web.django.swagger import Params, ParamsTypes, Query
from project_utils.web.django.view import SwaggerType
from ._types import REQUEST_QUERY, REQUEST_BODY, RESPONSE, REQUEST_FORM


class BaseDocumentType(metaclass=ABCMeta):
    path: REQUEST_QUERY
    query: REQUEST_QUERY
    form: REQUEST_FORM
    response_page: RESPONSE
    response_get: RESPONSE
    response_post: RESPONSE
    response_put: RESPONSE
    response_delete: RESPONSE = SwaggerType().response({
        "delete_count": Params(ParamsTypes.integer, title="删除数量").params()
    })
    base_query: REQUEST_QUERY = [
        Query("pagenum", require=True, description="分页页码").params(),
        Query("pagesize", require=True, description="分页大小").params(),
        Query("startTime", description="开始时间").params(),
        Query("endTime", description="截止时间").params()
    ]

    @classmethod
    @abstractmethod
    def body(cls, require: List[str]) -> REQUEST_BODY:
        ...

    @classmethod
    @abstractmethod
    def page(cls, properties: Dict) -> RESPONSE:
        ...
