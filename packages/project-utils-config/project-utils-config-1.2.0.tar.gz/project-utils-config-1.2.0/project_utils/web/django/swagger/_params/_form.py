from enum import Enum

from typing import Optional, Dict, Union, Any, List

from drf_yasg.openapi import Schema, Parameter, IN_FORM

from ._base import SwaggerParamsBase
from ._types import SwaggerParamsEnum


class SwaggerFormParams(SwaggerParamsBase):
    name: str
    type: Union[SwaggerParamsEnum, Any]
    require: bool
    description: Optional[str]
    position: str

    def __init__(self, name: str, type: Union[SwaggerParamsEnum, Any], require: bool = False,
                 description: Optional[str] = None):
        self.name = name
        self.type = type
        self.require = require
        self.description = description
        self.position = IN_FORM

    def params(self, properties: Optional[Dict[str, Schema]] = None, items: Schema = None) -> Union[Schema, Parameter]:
        return Parameter(name=self.name,
                         in_=self.position,
                         description=self.description,
                         required=self.require,
                         type=self.type)
