from datetime import datetime

from jose import jwt
from jose.constants import ALGORITHMS

from fastapi_pydentity.security.tokens._jwt_security_token import JwtSecurityToken


class JwtTokenHandler:
    @staticmethod
    def encode(token: JwtSecurityToken) -> str:
        return jwt.encode(
            claims=token.payload,
            **token.get_security_key(),
            headers=token.headers,
            access_token=token.access_token
        )

    @staticmethod
    def decode(
            token: str,
            key: str | dict,
            algorithms: str | list = ALGORITHMS.HS256,
            options: dict | None = None,
            issuer: str | None = None,
            audience: str | None = None,
            subject: str | None = None
    ) -> JwtSecurityToken:
        payload = jwt.decode(
            token,
            key=key,
            algorithms=algorithms,
            options=options,
            issuer=issuer,
            audience=audience,
            subject=subject
        )
        return JwtSecurityToken(
            key=key,
            algorithms=algorithms,
            issuer=payload.get("iss", None),
            audience=payload.get("aud", None),
            subject=payload.get("sub", None),
            principal=payload.get("verified_claims", None),
            not_before=datetime.fromtimestamp(payload["nbf"]) if "nbf" in payload else None,
            expires=datetime.fromtimestamp(payload["exp"]) if "exp" in payload else None,
            headers=jwt.get_unverified_headers(token)
        )
