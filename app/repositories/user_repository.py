from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.user import User


class UserRepository(BaseRepository[User]):
    """
    Repository class for User model.
    これは User Model用の repository 基本(きほん) クラスです。
    """

    def __init__(self, db: Session):
        super().__init__(db, User) 