"""User service wrapper."""

from app.services.common.common_base import BaseService
from app.infra.models.user import User
from app.infra.repo.user_repository import UserRepository


class UserService(BaseService[User]):
    """Service for User entity."""

    def __init__(self):
        super().__init__(UserRepository())

__all__ = ["UserService"] 