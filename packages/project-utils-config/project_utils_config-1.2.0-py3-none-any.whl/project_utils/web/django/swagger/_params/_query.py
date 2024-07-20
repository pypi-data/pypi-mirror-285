from typing import Optional, Union, Any, Dict

from drf_yasg.openapi import Schema, Parameter, IN_QUERY

from ._base import SwaggerParamsBase
from ._types import SwaggerParamsEnum


class SwaggerQueryParams(SwaggerParamsBase):
    name: str
    type: Union[SwaggerParamsEnum, Any]
    require: bool
    description: Optional[str]
    position: str

    def __init__(self, name: str, require: bool = False,
                 description: Optional[str] = None, position: str = IN_QUERY):
        self.name = name
        self.type = SwaggerParamsEnum.string
        self.require = require
        self.description = description
        self.position = position

    def params(self, properties: Optional[Dict[str, Schema]] = None, items: Schema = None) -> Union[Schema, Parameter]:
        return Parameter(
            name=self.name,
            in_=self.position,
            description=self.description,
            required=self.require,
            type=self.type
        )
