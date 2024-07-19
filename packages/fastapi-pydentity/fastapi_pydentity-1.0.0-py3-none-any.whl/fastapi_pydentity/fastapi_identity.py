import logging
from collections.abc import Iterable
from re import Pattern
from typing import Optional, Callable, Union

from fastapi import FastAPI
from starlette.authentication import AuthenticationError
from starlette.requests import HTTPConnection
from starlette.responses import Response, PlainTextResponse

from fastapi_pydentity.abc.stores import IUserStore, IRoleStore
from fastapi_pydentity.authentication import AuthenticationBackend, AuthenticationMiddleware
from fastapi_pydentity.authentication.cookies import CookieAuthenticationBackend
from fastapi_pydentity.authorization.authorization_provider import AuthorizationOptions, AuthorizationProvider
from fastapi_pydentity.authorization.exc import AuthorizationError
from fastapi_pydentity.exc import ArgumentNoneException, InvalidOperationException
from fastapi_pydentity.http_context import HttpContext
from fastapi_pydentity.identity_options import IdentityOptions
from fastapi_pydentity.infrastructure.abc.service_collection import IServiceCollection
from fastapi_pydentity.infrastructure.dependencies import (
    get_default_identity_error_describer,
    get_default_user_validator,
    get_default_password_validator,
    get_default_password_hasher,
    get_default_lookup_normalizer,
    get_default_role_validator,
    get_default_user_confirmation,
    get_default_user_manager,
    get_default_role_manager,
    get_default_user_claims_principal_factory,
    get_default_signin_manager,
    depends,
)
from fastapi_pydentity.infrastructure.identity_builder import IdentityBuilder
from fastapi_pydentity.infrastructure.types import DependencyCallable
from fastapi_pydentity.types import TUser, TRole
from fastapi_pydentity.utils import get_device_uuid


class FastAPIIdentity:
    def __init__(self, app: FastAPI, service_collection: IServiceCollection):
        self.__services = service_collection
        self.app = app

    @property
    def services(self):
        return self.__services

    def mount(self):
        self.app.dependency_overrides.update(self.services)

    def add_identity(
            self,
            user: type[TUser],
            role: type[TRole],
            get_user_store: DependencyCallable[IUserStore[TUser]],
            get_role_store: DependencyCallable[IRoleStore[TRole]],
            setup_action: Optional[Callable[[IdentityOptions], None]] = None
    ) -> IdentityBuilder:
        if get_user_store is None:
            raise ArgumentNoneException("get_user_store")

        if get_role_store is None:
            raise ArgumentNoneException("get_role_store")

        # Services used by identity
        self.add_authentication(
            backend=CookieAuthenticationBackend(get_device_uuid()),
            excluded_urls={
                self.app.openapi_url,
                self.app.docs_url,
                self.app.redoc_url
            }
        )

        # Singleton IdentityOptions
        _options = IdentityOptions()
        if setup_action is not None:
            setup_action(_options)

        self.services.add_service(depends.IdentityOptions, lambda: _options)
        self.services.add_service(depends.IUserStore, get_user_store)
        self.services.add_service(depends.IRoleStore, get_role_store)

        self.services.add_service(depends.IUserValidators, get_default_user_validator)
        self.services.add_service(depends.IPasswordValidators, get_default_password_validator)
        self.services.add_service(depends.IPasswordHasher, get_default_password_hasher)
        self.services.add_service(depends.ILookupNormalizer, get_default_lookup_normalizer)
        self.services.add_service(depends.IRoleValidators, get_default_role_validator)
        self.services.add_service(depends.IdentityErrorDescriber, get_default_identity_error_describer)
        self.services.add_service(depends.IUserConfirmation, get_default_user_confirmation)
        self.services.add_service(depends.IUserClaimsPrincipalFactory, get_default_user_claims_principal_factory)

        self.services.add_service(depends.UserManager, get_default_user_manager)
        self.services.add_service(depends.RoleManager, get_default_role_manager)
        self.services.add_service(depends.SignInManager, get_default_signin_manager)

        @self.app.exception_handler(InvalidOperationException)
        async def invalid_operation_exception_handler(request, exc):
            logging.getLogger("InvalidOperationException").error(str(exc))
            return PlainTextResponse(status_code=500)

        return IdentityBuilder(user, role, self.services)

    def add_authentication(
            self,
            backend: AuthenticationBackend,
            excluded_urls: Optional[Iterable[Union[Pattern, str]]] = None,
            on_error: Optional[Callable[[HTTPConnection, AuthenticationError], Response]] = None
    ):
        if backend is None:
            raise ArgumentNoneException("backend")

        self.app.add_middleware(
            AuthenticationMiddleware,
            backend=backend,
            excluded_urls=excluded_urls,
            on_error=on_error
        )
        HttpContext.backend = backend

    def add_authorization(self, configure: Optional[Callable[[AuthorizationOptions], None]] = None):
        _options = AuthorizationOptions()
        if configure is not None:
            configure(_options)

        AuthorizationProvider.options = _options

        @self.app.exception_handler(AuthorizationError)
        async def authorization_exception_handler(request, exc):
            return PlainTextResponse(str(exc), status_code=403)
