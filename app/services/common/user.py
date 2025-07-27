"""User service wrapper."""

from app.services.common.common_base import BaseService
from app.infra.models.user import User
from app.infra.repo.user_repository import UserRepository
from sqlalchemy.ext.asyncio import AsyncSession


class UserService(BaseService[User]):
    """Service for User entity."""

    def __init__(self, db: AsyncSession):
        # UserService特殊，只接收db而非uow，因为它可能在未登录状态下使用
        self._db = db
        super().__init__(UserRepository(db=db))

__all__ = ["UserService"] 