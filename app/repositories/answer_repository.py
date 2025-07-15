from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.answers import Answer


class AnswerRepository(BaseRepository[Answer]):
    """Repository class for Answer model.
    これは Answer Model用の repository 基本(きほん) クラスです。
    """

    def __init__(self, db: Session):
        super().__init__(db, Answer) 