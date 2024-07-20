from typing import Union

from django.db.models import *

from datetime import datetime

Int = Union[int, IntegerField]
Bool = Union[bool, BooleanField]
Byte = Union[bytes, BinaryField]
Float = Union[float, FloatField]
String = Union[str, CharField]

Long = Union[int, BigIntegerField]
File = FileField
Url = Union[str, URLField]
Email = Union[str, EmailField]
DateTime = Union[datetime, DateTimeField]
Json = Union[str, JSONField]
Text = Union[str, TextField]
