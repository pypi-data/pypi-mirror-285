import logging
from collections.abc import Iterable
from typing import Generic, Optional

from fastapi_pydentity.security import ClaimsPrincipal, ClaimTypes, Claim
from fastapi_pydentity.default_user_confirmation import IUserConfirmation, DefaultUserConfirmation
from fastapi_pydentity.exc import ArgumentNoneException, InvalidOperationException
from fastapi_pydentity.http_context import HttpContext
from fastapi_pydentity.identity_error import IdentityError
from fastapi_pydentity.identity_result import IdentityResult
from fastapi_pydentity.identity_options import IdentityOptions
from fastapi_pydentity.signin_result import SignInResult
from fastapi_pydentity.types import TUser
from fastapi_pydentity.user_claims_principal_factory import IUserClaimsPrincipalFactory
from fastapi_pydentity.user_manager import UserManager


class TwoFactorAuthenticationInfo:
    def __init__(self, user: TUser, login_provider: str):
        self.user = user
        self.login_provider = login_provider


class SignInManager(Generic[TUser]):
    """Provides the APIs for user sign in."""

    def __init__(
            self,
            user_manager: UserManager[TUser],
            context: HttpContext,
            *,
            claims_factory: IUserClaimsPrincipalFactory[TUser],
            confirmation: IUserConfirmation[TUser],
            options: Optional[IdentityOptions] = None,
            logger: Optional[logging.Logger] = None,
    ):
        if user_manager is None:
            raise ArgumentNoneException("user_manager")
        if claims_factory is None:
            raise ArgumentNoneException("claims_factory")

        self._context = context
        self.user_manager: UserManager[TUser] = user_manager
        self.options: IdentityOptions = options or IdentityOptions()
        self.claims_factory: IUserClaimsPrincipalFactory[TUser] = claims_factory
        self._confirmation = confirmation or DefaultUserConfirmation()
        self.logger: logging.Logger = logger or logging.Logger(self.__class__.__name__)

    @property
    def context(self):
        if self._context is None:
            raise InvalidOperationException("HttpContext must not be None.")
        return self._context

    async def create_user_principal(self, user: TUser) -> ClaimsPrincipal:
        """

        :param user:
        :return:
        """
        return await self.claims_factory.create(user)

    async def can_sign_in(self, user: TUser) -> bool:
        """
        Returns a flag indicating whether the specified user can sign in.

        :param user: The user whose sign-in status should be returned.
        :return:
        """
        if (
                self.options.SignIn.REQUIRE_CONFIRMED_EMAIL and
                not await self.user_manager.is_email_confirmed(user)
        ):
            self.logger.debug("User cannot sign in without a confirmed email.")
            return False

        if (
                self.options.SignIn.REQUIRED_CONFIRMED_PHONE_NUMBER and
                not await self.user_manager.is_phone_number_confirmed(user)
        ):
            self.logger.debug("User cannot sign in without a confirmed phone number.")
            return False

        if (
                self.options.SignIn.REQUIRE_CONFIRMED_ACCOUNT and
                not await self._confirmation.is_confirmed(self.user_manager, user)
        ):
            self.logger.debug("User cannot sign in without a confirmed account.")
            return False

        return True

    async def sign_in(
            self,
            user: TUser,
            authentication_method: Optional[str] = None,
            *additional_claims: Claim
    ):
        if authentication_method:
            additional_claims = [*additional_claims, Claim(ClaimTypes.AuthenticationMethod, authentication_method)]
        return await self.sign_in_with_claims(user, additional_claims)

    async def refresh_sign_in(self, user: TUser):
        claims = []
        auth = await self.context.authenticate()
        authentication_method = auth.find_first(ClaimTypes.AuthenticationMethod)
        amr = auth.find_first("amr")

        if authentication_method:
            claims.append(authentication_method)
        if amr:
            claims.append(amr)

        await self.sign_in_with_claims(user, claims)

    async def sign_in_with_claims(self, user: TUser, additional_claims: Iterable[Claim]):
        user_principal = await self.create_user_principal(user)
        user_principal.identity.add_claims(*additional_claims)
        response = await self.context.sign_in(user_principal)
        self.context.user = user_principal
        return response

    async def sign_out(self):
        await self.context.sign_out()

    async def validate_security_stamp(self, principal: ClaimsPrincipal):
        if principal is None:
            return None

        user = await self.user_manager.get_user(principal)

        if await self.is_valid_security_stamp(
                user,
                principal.find_first_value(ClaimTypes.SecurityStamp)
        ):
            return user

        self.logger.debug("Failed to validate a security stamp.")
        return None

    async def is_valid_security_stamp(self, user: TUser, security_stamp: str) -> bool:
        """
        Validates the security stamp for the specified user.
        If no user is specified, or if the stores does not support security stamps, validation is considered successful.

        :param user: The user whose stamp should be validated.
        :param security_stamp: The expected security stamp value.
        :return: The result of the validation.
        """
        return (
                user is not None and
                # Only validate the security stamp if the store supports it
                (
                        not self.user_manager.supports_user_security_stamp or
                        security_stamp == await self.user_manager.get_security_stamp(user)
                )
        )

    async def is_two_factor_enabled(self, user: TUser) -> bool:
        return (
                self.user_manager.supports_user_two_factor and
                await self.user_manager.get_two_factor_enabled(user) and
                len(await self.user_manager.get_valid_two_factor_providers(user)) > 0
        )

    async def password_sign_in(
            self,
            username: str,
            password: str,
            lockout_on_failure: bool = True
    ) -> tuple[SignInResult, Optional[TUser]]:
        """

        :param username:
        :param password:
        :param lockout_on_failure:
        :return:
        """
        user = await self.user_manager.find_by_name(username)

        if user is None:
            return SignInResult.failed(), user

        attempt = await self.check_password_sign_in(user, password, lockout_on_failure)
        # if attempt.succeeded:
        #     return await self.sign_in_two_factor(user)
        return attempt, user

    async def check_password_sign_in(
            self,
            user: TUser,
            password: str,
            lockout_on_failure: bool
    ) -> SignInResult:
        """

        :param user:
        :param password:
        :param lockout_on_failure:
        :return:
        """
        if user is None:
            raise ArgumentNoneException("user")

        if error := await self._pre_sign_in_check(user):
            return error

        if await self.user_manager.check_password(user, password):
            await self._reset_lockout_with_result(user)
            return SignInResult.success()

        self.logger.warning("User failed to provide the correct password.")

        if self.user_manager.supports_user_lockout and lockout_on_failure:
            increment_lockout_result = await self.user_manager.access_failed(user)

            if not increment_lockout_result.succeeded:
                return SignInResult.failed()

            if await self.user_manager.is_locked_out(user):
                return await self._locked_out(user)

        return SignInResult.failed()

    async def _is_locked_out(self, user: TUser) -> bool:
        """
        Used to determine if a user is considered locked out.

        :param user: The user.
        :return:
        """
        return self.user_manager.supports_user_lockout and await self.user_manager.is_locked_out(user)

    async def _reset_lockout_with_result(self, user: TUser):
        """
        Used to reset a user's lockout count.

        :param user: The user.
        :return:
        """
        if self.user_manager.supports_user_lockout:
            result = await self.user_manager.reset_access_failed_count(user)

            if not result.succeeded:
                return IdentityResult.failed(
                    IdentityError("ResetLockout", "ResetLockout failed."),
                    *result.errors
                )

    async def _locked_out(self, user: TUser) -> SignInResult:  # noqa
        """
        Returns a locked out SignInResult.

        :param user:
        :return:
        """
        self.logger.warning("User is currently locked out.")
        return SignInResult.locked_out()

    async def _pre_sign_in_check(self, user: TUser) -> Optional[SignInResult]:
        """
        Used to ensure that a user is allowed to sign in.

        :param user:
        :return:
        """
        if not await self.can_sign_in(user):
            return SignInResult.failed()

        if await self._is_locked_out(user):
            return await self._locked_out(user)

        return None

    # TODO
    async def sign_in_or_two_factor(
            self,
            user: TUser,
            login_provider: Optional[str] = None,
            bypass_two_factor: bool = False
    ):
        if not bypass_two_factor and await self.is_two_factor_enabled(user):
            pass
        if login_provider:
            await self.context.sign_out()
        if login_provider is None:
            await self.sign_in_with_claims(user, [Claim("amr", "pwd")])
        else:
            await self.sign_in(user)

    async def do_two_factor_sign_in(self, user: TUser, two_factor_info: TwoFactorAuthenticationInfo):
        reset_lockout_result = await self._reset_lockout_with_result(user)
        if not reset_lockout_result.succeeded:
            return SignInResult.failed()

        claims = [Claim("amr", "mfa")]

        if two_factor_info.login_provider:
            claims.append(Claim(ClaimTypes.AuthenticationMethod, two_factor_info.login_provider))

        return await self.sign_in_with_claims(user, claims)

    async def retrieve_two_factor_info(self) -> Optional[TwoFactorAuthenticationInfo]:
        result = await self.context.authenticate()

        user_id = result.find_first_value(ClaimTypes.Name)
        if not user_id:
            return None

        user = await self.user_manager.find_by_id(user_id)
        if not user:
            return None

        return TwoFactorAuthenticationInfo(user, result.find_first_value(ClaimTypes.AuthenticationMethod))


    async def two_factor_sign_in(self, provider: str, code: str):
        two_factor_info = await self.retrieve_two_factor_info()
        if not two_factor_info:
            return SignInResult.failed()

        user = two_factor_info.user

        if error := await self._pre_sign_in_check(user):
            return error

        if await self.user_manager.verify_two_factor_token(user, provider, code):
            return self.do_two_factor_sign_in(user, two_factor_info)

        if self.user_manager.supports_user_lockout:
            increment_lockout_result = await self.user_manager.access_failed(user)

            if not increment_lockout_result.succeeded:
                return SignInResult.failed()

            if await self.user_manager.is_locked_out(user):
                return await self._locked_out(user)

        return SignInResult.failed()
