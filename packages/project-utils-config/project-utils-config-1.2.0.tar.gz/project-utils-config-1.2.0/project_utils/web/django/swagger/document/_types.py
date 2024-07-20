from enum import Enum
from typing import List, Dict, Union

from drf_yasg.openapi import Parameter, Schema

REQUEST_QUERY = Union[List[Parameter], Enum]
REQUEST_BODY = Union[Schema, Enum]
REQUEST_FORM = Union[List[Parameter], Enum]
RESPONSE = Union[Dict[str, Schema], Enum]