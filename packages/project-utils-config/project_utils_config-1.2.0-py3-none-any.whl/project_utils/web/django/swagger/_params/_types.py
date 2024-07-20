from enum import Enum

from drf_yasg import openapi


class SwaggerParamsEnum(Enum):
    object: str = openapi.TYPE_OBJECT
    string: str = openapi.TYPE_STRING
    number: str = openapi.TYPE_NUMBER
    integer: str = openapi.TYPE_INTEGER
    boolean: str = openapi.TYPE_BOOLEAN
    array: str = openapi.TYPE_ARRAY
    file: str = openapi.TYPE_FILE


if __name__ == '__main__':
    print(SwaggerParamsEnum.file)
