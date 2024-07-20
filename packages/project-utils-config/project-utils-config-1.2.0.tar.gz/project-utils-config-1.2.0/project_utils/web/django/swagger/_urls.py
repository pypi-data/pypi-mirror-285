from typing import Callable, Any

from drf_yasg.openapi import Info
from drf_yasg.views import get_schema_view

from .config import SwaggerConfig

swagger_view_callable: Callable[[SwaggerConfig], Any] = lambda config: get_schema_view(Info(**config.swagger.to_dict()))
