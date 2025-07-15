from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.mistake import Mistake


class MistakeRepository(BaseRepository[Mistake]):
    """Repository class for Mistake model.
    これは Mistake Model用の repository 基本(きほん) クラスです。
    """

    def __init__(self, db: Session):
        super().__init__(db, Mistake) 