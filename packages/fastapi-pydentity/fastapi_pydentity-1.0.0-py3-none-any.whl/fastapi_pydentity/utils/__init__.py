import inspect
from uuid import NAMESPACE_DNS, UUID, uuid5, getnode

from ._dataclasses import asdict
from ._datetime import datetime


def is_none_or_empty(_string: str | None, /) -> bool:
    return _string is None or not _string or _string.isspace()


def get_device_uuid() -> str:
    return str(uuid5(NAMESPACE_DNS, str(UUID(int=getnode()))))


def funcname():
    return inspect.currentframe().f_code.co_name
