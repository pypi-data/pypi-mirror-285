from collections.abc import Iterable

from fastapi_pydentity.abc import (
    IUserValidator,
    IUserClaimsPrincipalFactory,
    IPasswordValidator,
    IRoleValidator,
    IUserConfirmation,
    IUserTwoFactorTokenProvider
)
from fastapi_pydentity.abc.stores import IUserStore, IRoleStore
from fastapi_pydentity.identity_error_describer import IdentityErrorDescriber
from fastapi_pydentity.identity_options import TokenOptions
from fastapi_pydentity.infrastructure.abc.service_collection import IServiceCollection
from fastapi_pydentity.infrastructure.dependencies import depends
from fastapi_pydentity.infrastructure.types import DependencyCallable
from fastapi_pydentity.token_provider import (
    DefaultTokenProvider,
    EmailTokenProvider,
    PhoneNumberTokenProvider
)
from fastapi_pydentity.types import TUser, TRole


class IdentityBuilder:
    def __init__(self, user: type[TUser], role: type[TRole], services: IServiceCollection):
        self.user = user
        self.role = role
        self.__services = services

    def add_user_validator(self, get_validators: DependencyCallable[Iterable[IUserValidator[TUser]]]):
        self.__services.add_service(depends.IUserValidators, get_validators)
        return self

    def add_user_claims_principal_factory(self, get_factory: DependencyCallable[IUserClaimsPrincipalFactory[TUser]]):
        self.__services.add_service(depends.IUserClaimsPrincipalFactory, get_factory)
        return self

    def add_identity_error_describer(self, get_describer: DependencyCallable[IdentityErrorDescriber]):
        self.__services.add_service(depends.IdentityErrorDescriber, get_describer)
        return self

    def add_password_validator(self, get_validators: DependencyCallable[Iterable[IPasswordValidator[TUser]]]):
        self.__services.add_service(depends.IPasswordValidators, get_validators)
        return self

    def add_user_store(self, get_store: DependencyCallable[IUserStore[TUser]]):
        self.__services.add_service(depends.IUserStore, get_store)
        return self

    def add_user_manager[TUserManager](self, get_manager: DependencyCallable[TUserManager]):
        self.__services.add_service(depends.UserManager, get_manager)
        return self

    def add_role_validator(self, get_validators: DependencyCallable[Iterable[IRoleValidator[TRole]]]):
        self.__services.add_service(depends.IRoleValidators, get_validators)
        return self

    def add_role_store(self, get_store: DependencyCallable[IRoleStore[TRole]]):
        self.__services.add_service(depends.IRoleStore, get_store)
        return self

    def add_role_manager[TRoleManager](self, get_manager: DependencyCallable[TRoleManager]):
        self.__services.add_service(depends.RoleManager, get_manager)
        return self

    def add_user_confirmation(self, get_confirmation: DependencyCallable[IUserConfirmation[TUser]]):
        self.__services.add_service(depends.IUserConfirmation, get_confirmation)
        return self

    def add_token_provider(self, provider_name: str, provider: IUserTwoFactorTokenProvider[TUser]):
        self.__services.get(depends.IdentityOptions)().Tokens.PROVIDER_MAP[provider_name] = provider
        return self

    def add_default_token_providers(self):
        self.add_token_provider(TokenOptions.DEFAULT_PROVIDER, DefaultTokenProvider())
        self.add_token_provider(TokenOptions.DEFAULT_EMAIL_PROVIDER, EmailTokenProvider())
        self.add_token_provider(TokenOptions.DEFAULT_PHONE_PROVIDER, PhoneNumberTokenProvider())
        return self

    def add_signin_manager[TSignInManager](self, get_manager: DependencyCallable[TSignInManager]):
        self.__services.add_service(depends.SignInManager, get_manager)
        return self
