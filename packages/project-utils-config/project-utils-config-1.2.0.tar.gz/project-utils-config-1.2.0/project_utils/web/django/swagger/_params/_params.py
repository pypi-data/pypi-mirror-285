from typing import Optional, List, Dict, Any, Union

from drf_yasg.openapi import Schema

from ._base import SwaggerParamsBase
from ._types import SwaggerParamsEnum


class SwaggerParams(SwaggerParamsBase):
    type: Union[SwaggerParamsEnum, Any]
    title: Optional[str]
    require: Optional[List[str]]
    description: Optional[str]
    properties: Optional[Dict[str, Schema]]

    def __init__(self, type: Union[SwaggerParamsEnum, Any], title: Optional[str] = None,
                 require: Optional[List[str]] = None,
                 description: Optional[str] = None):
        """

        :rtype: object
        """
        self.type = type
        self.title = title
        self.require = require
        self.description = description

    def params(self, properties: Optional[Dict[str, Schema]] = None, items: Schema = None) -> Union[Schema]:
        return Schema(
            title=self.title,
            type=self.type.value,
            required=self.require,
            description=self.description,
            properties=properties,
            items=items
        )


if __name__ == '__main__':
    from drf_yasg.openapi import TYPE_OBJECT
