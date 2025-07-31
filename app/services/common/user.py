"""User service wrapper."""

from app.services.common.common_base import BaseService
from app.infra.models.user import User
from app.infra.repo.user_repository import UserRepository
from app.infra.context import uow_ctx


class UserService(BaseService[User]):
    """Service for User entity."""

    def __init__(self):
        self._uow = uow_ctx.get()
        self._repo : UserRepository = UserRepository(db=self._uow.db)
        super().__init__(self._repo)
        
    async def get_current_user(self) -> User:
        return await self._repo.get_by_id(self._uow.current_user.id)

__all__ = ["UserService"] 