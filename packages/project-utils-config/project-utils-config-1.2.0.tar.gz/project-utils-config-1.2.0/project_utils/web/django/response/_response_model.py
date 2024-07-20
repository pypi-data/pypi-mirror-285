import json

from django.http.response import JsonResponse, HttpResponse
from rest_framework.response import Response

from ._response_types import BODYTYPE, DATATYPE, ERRTYPE


class ResponseModel:
    status: int
    body: BODYTYPE
    data: DATATYPE
    error: ERRTYPE

    def __init__(self, status: int = 200, data: DATATYPE = None, error: ERRTYPE = None):
        errno: int = 0 if 200 <= status < 300 else -1
        errmsg: str = "success" if errno == 0 else "failed"
        self.status = status
        if data is not None:
            self.data = data
        if error is not None:
            self.error = error

        self.body = {"errno": str(errno), "errmsg": errmsg}
        if hasattr(self, "data") and self.data:
            self.body['data'] = data
        print(hasattr(self, "error") and self.error)
        if hasattr(self, "error") and self.error:
            self.body['error'] = error.error_summary

    def to_dict(self) -> BODYTYPE:
        return self.body

    def to_json(self):
        return json.dumps(self.to_dict(), ensure_ascii=False)

    def to_response(self) -> HttpResponse:
        return JsonResponse(status=self.status, data=self.body)

    def to_rest_response(self) -> Response:
        return Response(status=self.status, data=self.to_dict())
