import asyncio
import traceback

from asgiref.sync import async_to_sync
from django.http.request import HttpRequest
from django.http.response import HttpResponse

from project_utils.exception import ViewException, ModelException
from project_utils.web.django.conf import DjangoConfig
from project_utils.web.django.request import WebRequest
from project_utils.web.django.response import WebResponse

from .api_util import BaseAPIUtil

from .._types import BASE_API_TYPE, VIEW_TYPE, API_VIEW_HANDLER_TYPE


def base_api(config: DjangoConfig, method: str = "get") -> BASE_API_TYPE:
    def decorator(fun: VIEW_TYPE) -> API_VIEW_HANDLER_TYPE:
        def handler(request: HttpRequest, *args: ..., **kwargs: ...) -> HttpResponse:
            try:
                api_util: BaseAPIUtil = BaseAPIUtil(config=config, request=request, method=method)
            except ViewException as e:
                config.printf.error(e.error_detail)
                config.printf.warning(e.error_summary)
                return WebResponse(status=e.status, error=e).to_response()
            except ModelException as e:
                config.printf.error(e.error_detail)
                config.printf.warning(e.error_summary)
                return WebResponse(status=404, error=e).to_response()
            except Exception as e:
                view_exception: ViewException = ViewException(405, str(e), traceback.format_exc())
                config.printf.error(view_exception.error_detail)
                config.printf.warning(view_exception.error_summary)
                return WebResponse(status=view_exception.status, error=view_exception).to_response()
            try:
                web_request: WebRequest = api_util.request_init(config)
            except ViewException as e:
                config.printf.error(e.error_detail)
                config.printf.warning(e.error_summary)
                return WebResponse(status=e.status, error=e).to_response()
            except Exception as e:
                view_exception: ViewException = ViewException(403, str(e), traceback.format_exc())
                config.printf.error(view_exception.error_detail)
                config.printf.warning(view_exception.error_summary)
                return WebResponse(status=view_exception.status, error=view_exception).to_response()
            try:
                if asyncio.iscoroutinefunction(fun):
                    web_response: WebResponse = async_to_sync(fun)(web_request, *args, **kwargs)
                else:
                    web_response: WebResponse = fun(web_request, *args, **kwargs)
            except ViewException as e:
                config.printf.error(e.error_detail)
                config.printf.warning(e.error_summary)
                return WebResponse(status=e.status, error=e).to_response()
            except Exception as e:
                view_exception: ViewException = ViewException(410, str(e), traceback.format_exc())
                config.printf.error(view_exception.error_detail)
                config.printf.warning(view_exception.error_summary)
                return WebResponse(status=view_exception.status, error=view_exception).to_response()
            return web_response.to_response()

        return handler

    return decorator
