import dataclasses
from abc import abstractmethod
from typing import TYPE_CHECKING

from fastapi import Request, Response
from fastapi.security.base import SecurityBase
from starlette.authentication import AuthenticationError

from fastapi_pydentity.security.claims import ClaimsPrincipal

if TYPE_CHECKING:
    from fastapi_pydentity.http_context import HttpContext


class AuthenticationBackend:
    def __init__(self, scheme: SecurityBase, secret: str):
        self.scheme = scheme
        self.__secret = secret

    async def authenticate(self, request: Request) -> ClaimsPrincipal:
        if token := await self.scheme(request):  # noqa
            return await self._authenticate(request, token)
        raise AuthenticationError()

    @abstractmethod
    async def _authenticate(self, request: Request, token: str) -> ClaimsPrincipal:
        pass

    @abstractmethod
    async def sign_in(self, context: "HttpContext", user: ClaimsPrincipal) -> Response:
        pass

    @abstractmethod
    async def sign_out(self, context: "HttpContext") -> None:
        pass
