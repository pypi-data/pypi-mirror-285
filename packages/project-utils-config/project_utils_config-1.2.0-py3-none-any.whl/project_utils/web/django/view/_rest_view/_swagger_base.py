from abc import ABCMeta

from typing import List, Dict, Union, Optional

from drf_yasg.openapi import Parameter, Schema

from project_utils.web.django.swagger import ResponseType, ResponseSchema, ParamsTypes


class SwaggerTypeBase(metaclass=ABCMeta):
    request_get: List[Parameter]
    request_post: Schema
    request_put: Schema
    request_delete: Dict[str, Union[List[Parameter], Schema, None]] = {
        "query": [],
        "params": None
    }

    def __init__(
            self, *,
            request_get: Optional[List[Parameter]] = None,
            request_post: Optional[Schema] = None,
            request_put: Optional[Schema] = None,
            request_delete: Optional[Dict[str, Union[List[Parameter], Schema, None]]] = None,
    ):
        self.request_get = request_get
        self.request_post = request_post
        self.request_put = request_put
        if request_delete:
            self.request_delete = request_delete

    def response(self, properties: Optional[Dict[str, Schema]] = None, items: Optional[Schema] = None) -> Dict[
        Union[str, int], Schema]:
        return {
            200: ResponseType().success(properties=properties, items=items),
            400: ResponseType().error()
        }
