from abc import ABCMeta
from typing import Union, Tuple, Dict

from django.db.models import Model


class BaseMeta(metaclass=ABCMeta):
    model: Model
    fields: Union[str, Tuple] = "__all__"
    exclude: Tuple = ()
    read_only_fields: Tuple = ("id",)
    extra_kwargs: Dict = {}
