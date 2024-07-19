import base64
import json
import uuid
from datetime import datetime, timedelta, UTC
from typing import TYPE_CHECKING, Callable, Optional, Literal, Any, Generator

from fastapi import Request, Response
from fastapi.security import APIKeyCookie
from jose import jwt, JWTError
from starlette.authentication import AuthenticationError

from fastapi_pydentity.abc.personal_data_protector import IPersonalDataProtector
from fastapi_pydentity.authentication.base import AuthenticationBackend
from fastapi_pydentity.authentication.token_validation_parameters import TokenValidationParameters
from fastapi_pydentity.default_personal_data_protector import DefaultPersonalDataProtector
from fastapi_pydentity.http.cookie_options import CookieOptions
from fastapi_pydentity.security.claims import ClaimsPrincipal, ClaimTypes
from fastapi_pydentity.utils import asdict

if TYPE_CHECKING:
    from fastapi_pydentity.http_context import HttpContext


class CookieAuthenticationBackend(AuthenticationBackend):
    def __init__(
            self,
            secret: str,
            cookie_name: str = ".fastapi.identity.auth",
            expires: Optional[timedelta] = None,
            *,
            path: str = "/",
            domain: Optional[str] = None,
            secure: bool = True,
            httponly: bool = True,
            samesite: Optional[Literal["lax", "strict", "none"]] = "lax",
            valid_audience: str = "LOCALHOST AUTHORITY",
            valid_issuer: str = "LOCALHOST AUTHORITY",
            configure_validation_parameters: Optional[Callable[[TokenValidationParameters], None]] = None,
            claim_cookie_prefix: str = ".fastapi.identity.client.",
            data_protector: Optional[type[IPersonalDataProtector]] = DefaultPersonalDataProtector
    ):
        super().__init__(
            scheme=APIKeyCookie(name=cookie_name, scheme_name="identity.application", auto_error=False),
            secret=secret
        )
        self._authentication_cookie_name = cookie_name
        self._expires = expires
        self._valid_audience = valid_audience
        self._valid_issuer = valid_issuer
        self._token_validation_parameters = TokenValidationParameters()
        self._claim_cookie_prefix = claim_cookie_prefix
        self._data_protector = data_protector
        self._cookie_options = CookieOptions(
            path=path,
            domain=domain,
            secure=secure,
            httponly=httponly,
            samesite=samesite
        )

        if configure_validation_parameters is not None:
            configure_validation_parameters(self._token_validation_parameters)

    async def _authenticate(self, request: Request, token: str) -> ClaimsPrincipal:
        try:
            jwt.decode(
                token=token,
                key=self.__secret,
                algorithms="HS256",
                options=asdict(self._token_validation_parameters),
                audience=self._valid_audience,
                issuer=self._valid_issuer
            )
        except JWTError:
            raise AuthenticationError()

        return self._create_claims_principal(request)

    async def sign_in(self, context: "HttpContext", user: ClaimsPrincipal) -> Response:
        await self.sign_out(context)
        context.response.status_code = 200
        context.response.headers.append("Cache-Control", "no-cache, no-store")
        expires = datetime.now(UTC) + self._expires if self._expires is not None else None
        self._cookie_options.expires = expires

        data = {
            "exp": expires,
            "aud": self._valid_audience,
            "iss": self._valid_issuer,
            "sub": user.find_first_value(ClaimTypes.NameIdentifier)
        }

        context.response.set_cookie(
            key=self._authentication_cookie_name,
            value=jwt.encode(data, self.__secret),
            **asdict(self._cookie_options)
        )

        for claim in self.encode_claims(user.dump()):
            context.response.set_cookie(
                key=self._generate_random_cookie_name(),
                value=claim,
                **asdict(self._cookie_options)
            )

        return context.response

    async def sign_out(self, context: "HttpContext") -> None:
        context.response.status_code = 200
        context.response.delete_cookie(self._authentication_cookie_name)
        for cookie_name, cookie_value in context.request.cookies.items():
            if self._cookie_is_claim(cookie_name):
                context.response.delete_cookie(key=cookie_name)

    def protect_data(self, data: str, purpose: str) -> str:
        data_protector = self._data_protector.create_protector(purpose)
        protected_data = data_protector.protect(data)
        b64_protected_data = base64.urlsafe_b64encode(protected_data.encode())
        return b64_protected_data.decode()

    def unprotect_data(self, data: str, purpose: str) -> str:
        data_protector = self._data_protector.create_protector(purpose)
        protected_data = base64.urlsafe_b64decode(data)
        unprotected_data = data_protector.unprotect(protected_data.decode())
        return unprotected_data

    def encode_claims(self, principal: list[dict[str, Any]]) -> Generator[str, Any, None]:
        protect_data = self.protect_data if self._data_protector is not None else self.__default_protect_data
        for identity in principal:
            for claim in identity["claims"]:
                claim["authentication_type"] = identity["authentication_type"]
                claim["name_type"] = identity["name_type"]
                claim["role_type"] = identity["role_type"]
                yield protect_data(json.dumps(claim), "Claim")

    def decode_claims(self, principal: list[str]) -> list[dict[str, Any]]:
        identities: list[dict[str, Any]] = []
        unprotect_data = self.unprotect_data if self._data_protector is not None else self.__default_protect_data

        for claim in principal:
            decoded_claim = json.loads(unprotect_data(claim, "Claim"))
            authentication_type = decoded_claim.pop("authentication_type", None)
            name_type = decoded_claim.pop("name_type", None)
            role_type = decoded_claim.pop("role_type", None)

            exists = False
            index = None

            for i, identity in enumerate(identities):
                if (
                        identity["authentication_type"] == authentication_type and
                        identity["name_type"] == name_type and
                        identity["role_type"] == role_type
                ):
                    exists = True
                    index = i
                    break

            if not exists:
                identity = {
                    "authentication_type": authentication_type,
                    "name_type": name_type,
                    "role_type": role_type,
                    "claims": [decoded_claim]
                }
                identities.append(identity)
            else:
                identities[index]["claims"].append(decoded_claim)

        return identities

    def _generate_random_cookie_name(self) -> str:
        return self._claim_cookie_prefix + str(uuid.uuid4())

    def _create_claims_principal(self, request: Request):
        encoded_claims = []
        for cookie_name, cookie_value in request.cookies.items():
            if self._cookie_is_claim(cookie_name):
                encoded_claims.append(cookie_value)
        return ClaimsPrincipal.from_list(self.decode_claims(encoded_claims))

    def _cookie_is_claim(self, name: str) -> bool:
        return name.startswith(self._claim_cookie_prefix)

    def __default_protect_data(self, data, *args):
        return data
