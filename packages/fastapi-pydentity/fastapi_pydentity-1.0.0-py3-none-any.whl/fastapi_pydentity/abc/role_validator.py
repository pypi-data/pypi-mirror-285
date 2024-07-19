from abc import ABC, abstractmethod
from typing import Generic, TYPE_CHECKING

from fastapi_pydentity.identity_result import IdentityResult
from fastapi_pydentity.types import TRole

if TYPE_CHECKING:
    from fastapi_pydentity.role_manager import RoleManager


class IRoleValidator(Generic[TRole], ABC):
    """Provides an abstraction for a validating a role."""

    @abstractmethod
    async def validate(self, manager: "RoleManager[TRole]", role: TRole) -> IdentityResult:
        """
        Validates a role as an asynchronous operation.

        :param manager: The RoleManager[TRole] that can be used to retrieve role properties.
        :param role: The roel to validate.
        :return:
        """
