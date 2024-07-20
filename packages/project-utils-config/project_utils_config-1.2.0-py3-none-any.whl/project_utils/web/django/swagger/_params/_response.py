from copy import deepcopy
from typing import Optional, Union, Any, Dict

from drf_yasg.openapi import Schema

from ._base import SwaggerParamsBase
from ._types import SwaggerParamsEnum


class SwaggerParamsResponse:
    class SwaggerParamsResponseInner(SwaggerParamsBase):
        type: str = SwaggerParamsEnum.object
        title: Optional[str]
        description: Optional[str]

        def __init__(self, type: Union[SwaggerParamsEnum, Any], title: Optional = None,
                     description: Optional[str] = None):
            self.type = type.value
            self.title = title
            self.description = description

        def params(self, properties: Optional[Dict[str, Schema]] = None, items: Schema = None) -> Union[Schema]:
            return Schema(type=self.type, title=self.title, description=self.description, properties=properties,
                          items=items)

    inner = SwaggerParamsResponseInner
    base: Dict[str, Schema] = {
        "errno": inner(SwaggerParamsEnum.string, title="响应码", description="响应码").params(),
        "errmsg": inner(SwaggerParamsEnum.string, title="响应描述", description="响应描述").params()
    }

    def success(self, properties: Optional[Dict[str, Schema]] = None, items: Optional[Schema] = None) -> Schema:
        base: Dict[str, Schema] = deepcopy(self.base)
        if properties:
            base.update({
                "data": self.inner(SwaggerParamsEnum.object, description="响应数据").params(properties=properties)
            })
        if items:
            base.update({
                "data": self.inner(SwaggerParamsEnum.array, description="响应数据").params(items=items)
            })
        return Schema(type=SwaggerParamsEnum.object.value, properties=base)

    def error(self) -> Schema:
        base: Dict[str, Schema] = deepcopy(self.base)
        base.update({
            "error": self.inner(SwaggerParamsEnum.string, "错误信息").params()
        })
        return Schema(type=SwaggerParamsEnum.object.value, properties=base)
