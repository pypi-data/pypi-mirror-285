from fastapi import Depends

from fastapi_pydentity.default_user_confirmation import DefaultUserConfirmation
from fastapi_pydentity.identity_error_describer import IdentityErrorDescriber
from fastapi_pydentity.http_context import HttpContext
from fastapi_pydentity.lookup_normalizer import UpperLookupNormalizer
from fastapi_pydentity.password_hasher import PasswordHasher
from fastapi_pydentity.password_validator import PasswordValidator
from fastapi_pydentity.role_manager import RoleManager
from fastapi_pydentity.role_validator import RoleValidator
from fastapi_pydentity.signin_manager import SignInManager
from fastapi_pydentity.user_claims_principal_factory import UserClaimsPrincipalFactory
from fastapi_pydentity.user_manager import UserManager
from fastapi_pydentity.user_validator import UserValidator


class depends:
    class DbContext:
        pass

    class IdentityOptions:
        pass

    class IdentityErrorDescriber:
        pass

    class IUserStore:
        pass

    class IRoleStore:
        pass

    class IUserValidators:
        pass

    class IPasswordValidators:
        pass

    class IPasswordHasher:
        pass

    class ILookupNormalizer:
        pass

    class IRoleValidators:
        pass

    class IUserConfirmation:
        pass

    class IUserClaimsPrincipalFactory:
        pass

    class UserManager:
        pass

    class RoleManager:
        pass

    class SignInManager:
        pass


def get_default_identity_error_describer():
    yield IdentityErrorDescriber()


def get_default_user_validator(errors=Depends(depends.IdentityErrorDescriber)):
    yield [UserValidator(errors)]


def get_default_password_validator(errors=Depends(depends.IdentityErrorDescriber)):
    yield [PasswordValidator(errors)]


def get_default_password_hasher():
    yield PasswordHasher()


def get_default_lookup_normalizer():
    yield UpperLookupNormalizer()


def get_default_role_validator(errors=Depends(depends.IdentityErrorDescriber)):
    yield [RoleValidator(errors)]


def get_default_user_confirmation():
    yield DefaultUserConfirmation()


def get_default_user_manager(
        store=Depends(depends.IUserStore),
        options=Depends(depends.IdentityOptions),
        password_hasher=Depends(depends.IPasswordHasher),
        password_validators=Depends(depends.IPasswordValidators),
        user_validators=Depends(depends.IUserValidators),
        key_normalizer=Depends(depends.ILookupNormalizer),
        errors=Depends(depends.IdentityErrorDescriber)
):
    yield UserManager(
        store,
        options=options,
        password_hasher=password_hasher,
        password_validators=password_validators,
        user_validators=user_validators,
        key_normalizer=key_normalizer,
        errors=errors
    )


def get_default_role_manager(
        store=Depends(depends.IRoleStore),
        role_validators=Depends(depends.IRoleValidators),
        key_normalizer=Depends(depends.ILookupNormalizer),
        errors=Depends(depends.IdentityErrorDescriber)
):
    yield RoleManager(
        store,
        role_validators=role_validators,
        key_normalizer=key_normalizer,
        errors=errors
    )


def get_default_user_claims_principal_factory(
        user_manager=Depends(depends.UserManager),
        role_manager=Depends(depends.RoleManager)
):
    yield UserClaimsPrincipalFactory(user_manager, role_manager)


def get_default_signin_manager(
        context=Depends(HttpContext),
        user_manager=Depends(depends.UserManager),
        claims_factory=Depends(depends.IUserClaimsPrincipalFactory),
        confirmation=Depends(depends.IUserConfirmation),
        options=Depends(depends.IdentityOptions),
):
    yield SignInManager(
        user_manager,
        context=context,
        claims_factory=claims_factory,
        confirmation=confirmation,
        options=options
    )
