from ._document import BaseDocumentType
from ._types import REQUEST_BODY, REQUEST_QUERY, REQUEST_FORM, RESPONSE

BaseDocument = BaseDocumentType

__all__ = [
    "BaseDocument",
    "REQUEST_QUERY",
    "REQUEST_BODY",
    "REQUEST_FORM",
    "RESPONSE"
]
