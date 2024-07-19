import dataclasses
from typing import Any


def asdict(obj: Any, exclude_none: bool = True) -> dict[str, Any]:
    if exclude_none:
        return dataclasses.asdict(obj, dict_factory=lambda x: {k: v for (k, v) in x if v is not None})
    return dataclasses.asdict(obj)
