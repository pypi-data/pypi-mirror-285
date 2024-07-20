from abc import ABCMeta
from typing import Dict, List

from rest_framework.pagination import PageNumberPagination

from project_utils.web.django.utils import DjangoUtils


class BasePageNumberPagination(PageNumberPagination, metaclass=ABCMeta):
    page_query_param: str = "pagenum"
    page_size_query_param: str = "pagesize"
    page_size: int = 10

    @classmethod
    def get_paginate_option_name(cls) -> List[str]:
        return [cls.page_query_param, cls.page_size_query_param]

    async def async_paginate_queryset(self, queryset, request, view=None):
        return await DjangoUtils.to_async_fun(self.paginate_queryset, queryset, request, view)

    async def get_paginated_data(self, data):
        return self.get_paginated_response(data)

    def get_paginated_response(self, data) -> Dict[str, any]:
        return {
            "count": self.page.paginator.count,
            "next": self.get_next_link(),
            "previous": self.get_previous_link(),
            "results": data
        }
