from ._params import SwaggerParams
from ._query import SwaggerQueryParams
from ._response import SwaggerParamsResponse
from ._types import SwaggerParamsEnum
from ._form import SwaggerFormParams

params = Params = SwaggerParams
query = Query = SwaggerQueryParams
form = Form = SwaggerFormParams
response_type = ResponseType = SwaggerParamsResponse
response_schema = ResponseSchema = SwaggerParamsResponse.inner
params_types = ParamsTypes = SwaggerParamsEnum

__all__ = [
    "params",
    "Params",
    "query",
    "Query",
    "form",
    "Form",
    "response_type",
    "ResponseType",
    "response_schema",
    "ResponseSchema",
    "params_types",
    "ParamsTypes",
]
