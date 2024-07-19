from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Union, Literal


@dataclass
class CookieOptions:
    max_age: Optional[int] = None
    expires: Optional[Union[datetime, str, int]] = None
    path: str = "/"
    domain: Optional[str] = None
    secure: bool = False
    httponly: bool = False
    samesite: Optional[Literal["lax", "strict", "none"]] = "lax"
