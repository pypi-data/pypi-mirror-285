from dataclasses import dataclass


@dataclass
class TokenValidationParameters:
    verify_signature: bool = True
    verify_aud: bool = True
    verify_iat: bool = True
    verify_exp: bool = True
    verify_nbf: bool = True
    verify_iss: bool = True
    verify_sub: bool = True
    verify_jti: bool = True
    verify_at_hash: bool = True
    require_aud: bool = False
    require_iat: bool = False
    require_exp: bool = False
    require_nbf: bool = False
    require_iss: bool = False
    require_sub: bool = False
    require_jti: bool = False
    require_at_hash: bool = False
    leeway: int = 30
