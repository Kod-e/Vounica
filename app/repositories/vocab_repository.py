from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.vocab import Vocab


class VocabRepository(BaseRepository[Vocab]):
    """Repository class for Vocab model.
    これは Vocab Model用の repository 基本(きほん) クラスです。
    """

    def __init__(self, db: Session):
        super().__init__(db, Vocab) 