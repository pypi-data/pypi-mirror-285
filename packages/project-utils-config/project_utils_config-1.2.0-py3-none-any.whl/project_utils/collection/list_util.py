import copy

from typing import Union, List, Tuple, Any, Optional

COLLECTION: Any = Union[List, Tuple]


def index_of(
        array: COLLECTION,
        item: Any,
        start: int = 0,
        end: Optional[int] = None
) -> int:
    if end is None: end = len(array)
    try:
        return array.index(item, start, end)
    except:
        return -1


def replace_all(array: List, _old: Any, _new: Any) -> List:
    _array: List = copy.deepcopy(array)
    for i in range(len(_array)):
        if _array[i] == _old:
            _array[i] = _new
    return _array
