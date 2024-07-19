from typing import TYPE_CHECKING
from fastapi import Request, Response

if TYPE_CHECKING:
    from fastapi_pydentity.authentication.base import AuthenticationBackend
    from fastapi_pydentity.security.claims import ClaimsPrincipal


class HttpContext:
    backend: "AuthenticationBackend"

    def __init__(self, request: Request, response: Response):
        self.request = request
        self.response = response

    @property
    def user(self) -> "ClaimsPrincipal":
        return self.request.user

    @user.setter
    def user(self, value):
        self.request.scope['user'] = value

    async def authenticate(self):
        return await self.backend.authenticate(self.request)

    async def sign_in(self, principal: "ClaimsPrincipal"):
        return await self.backend.sign_in(self, principal)

    async def sign_out(self):
        return await self.backend.sign_out(self)

    async def get_authentication_service(self, name: str):
        pass
