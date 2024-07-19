from datetime import datetime
from typing import Optional, Any

from jose.constants import ALGORITHMS

from fastapi_pydentity.security.claims import ClaimsPrincipal


def jwt_encode_claims(principal: ClaimsPrincipal):
    if principal is None:
        return None

    identities = {}

    for identity in principal.dump():
        for claim in identity["claims"]:
            authentication_type = identity["authentication_type"]

            if authentication_type not in identities.keys():
                identities[authentication_type] = {}
                identities[authentication_type]["authentication_type"] = authentication_type
                identities[authentication_type]["name_type"] = identity["name_type"]
                identities[authentication_type]["role_type"] = identity["role_type"]
                identities[authentication_type]["claims"] = {}

            if claim["claim_type"] not in identities[authentication_type]["claims"].keys():
                identities[authentication_type]["claims"][claim["claim_type"]] = []

            key = claim.pop("claim_type")
            identities[authentication_type]["claims"][key].append(claim)

    return identities


def jwt_decode_claims(payload):
    if payload is None:
        return None

    identities = []

    for identity in payload.values():
        authentication_type = identity.pop("authentication_type", None)
        name_type = identity.pop("name_type", None)
        role_type = identity.pop("role_type", None)

        exists = False
        index = None

        for i, _identity in enumerate(identities):
            if (
                    _identity["authentication_type"] == authentication_type and
                    _identity["name_type"] == name_type and
                    _identity["role_type"] == role_type
            ):
                exists = True
                index = i
                break

        if not exists:
            create_identity = {
                "authentication_type": authentication_type,
                "name_type": name_type,
                "role_type": role_type,
                "claims": []
            }
            identities.append(create_identity)
            index = -1

        for key, values in identity["claims"].items():
            for claim in values:
                claim["claim_type"] = key
                identities[index]["claims"].append(claim)

    return ClaimsPrincipal.from_list(identities)


class JwtSecurityToken:
    def __init__(
            self,
            key: str | dict,
            algorithm: str = ALGORITHMS.HS256,
            issuer: str | None = None,
            audience: str | None = None,
            subject: str | None = None,
            principal: ClaimsPrincipal | dict | None = None,
            not_before: datetime | None = None,
            expires: datetime | None = None,
            headers: dict | None = None,
            access_token: str | None = None,
            **kwargs
    ):
        if expires and not_before:
            if not_before >= expires:
                raise ValueError("nbf >= exp")

        self._key = key
        self._algorithm = algorithm
        self._headers = headers
        self._access_token = access_token
        self._claims: dict[str, Any] = {}
        self._principal = principal

        if principal is None or isinstance(principal, ClaimsPrincipal):
            self._principal = principal
        elif isinstance(principal, dict):
            self._principal = jwt_decode_claims(principal)
        else:
            raise TypeError("dict[str, dict[str, ...]] or ClaimsPrincipal")

        self._claims.update(kwargs)

        if issuer:
            self._claims["iss"] = issuer
        if audience:
            self._claims["aud"] = audience
        if subject:
            self._claims["sub"] = subject
        if not_before:
            self._claims["nbf"] = not_before
        if expires:
            self._claims["exp"] = expires

    @property
    def principal(self) -> Optional[ClaimsPrincipal]:
        return self._principal

    @property
    def headers(self) -> Optional[dict]:
        return self._headers

    @property
    def payload(self) -> dict:
        self._claims.update(
            {"verified_claims": jwt_encode_claims(self.principal)}
        )
        return self._claims

    @property
    def access_token(self) -> Optional[str]:
        return self._access_token

    def get_security_key(self):
        return {"key": self._key, "algorithm": self._algorithm}

    def get_security_keys(self):
        return {"key": self._key, "algorithms": self._algorithm}
