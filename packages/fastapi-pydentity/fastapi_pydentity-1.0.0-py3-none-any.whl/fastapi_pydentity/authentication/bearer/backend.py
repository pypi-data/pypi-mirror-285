from typing import Callable, TYPE_CHECKING

from fastapi import Request, Response
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from jose.constants import ALGORITHMS
from starlette.authentication import AuthenticationError

from fastapi_pydentity.authentication.base import AuthenticationBackend, TokenValidationParameters
from fastapi_pydentity.identity_model.tokens.jwt import JwtTokenHandler
from fastapi_pydentity.security import ClaimsPrincipal
from fastapi_pydentity.utils import asdict

if TYPE_CHECKING:
    from fastapi_pydentity.http_context import HttpContext


class BearerAuthenticationBackend(AuthenticationBackend):
    def __init__(
            self,
            tokenUrl: str,
            secret: str,
            *,
            algorithms: list[str] | str = ALGORITHMS.HS256,
            valid_issuer: str | None = None,
            valid_audience: str | None = None,
            configure_validation_parameters: Callable[[TokenValidationParameters], None] | None = None
    ):
        super().__init__(
            scheme=OAuth2PasswordBearer(tokenUrl=tokenUrl, auto_error=False),
            secret=secret
        )
        self._algorithms = algorithms
        self._valid_audience = valid_audience
        self._valid_issuer = valid_issuer
        self._token_validation_parameters = TokenValidationParameters()

        if configure_validation_parameters is not None:
            configure_validation_parameters(self._token_validation_parameters)

    async def _authenticate(self, request: Request, token: str) -> ClaimsPrincipal:
        try:
            decoded_jwt = JwtTokenHandler.decode(
                token,
                key=self.__secret,
                algorithms=self._algorithms,
                options=asdict(self._token_validation_parameters),
                issuer=self._valid_issuer,
                audience=self._valid_audience
            )
        except JWTError as ex:
            raise AuthenticationError(ex)

        return decoded_jwt.principal

    async def sign_in(self, context: "HttpContext", user: ClaimsPrincipal) -> Response:
        pass

    async def sign_out(self, context: "HttpContext") -> None:
        pass
