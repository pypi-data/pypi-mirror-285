from abc import ABCMeta, abstractmethod

from typing import Optional, Dict, Union

from drf_yasg.openapi import Schema


class SwaggerParamsBase(metaclass=ABCMeta):
    @abstractmethod
    def params(self, properties: Optional[Dict[str, Schema]] = None, items: Schema = None) -> Union[Schema]:
        pass
