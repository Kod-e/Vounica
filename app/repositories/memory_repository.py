from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.memory import Memory


class MemoryRepository(BaseRepository[Memory]):
    """Repository class for Memory model.
    これは Memory Model用の repository 基本(きほん) クラスです。
    """

    def __init__(self, db: Session):
        super().__init__(db, Memory) 