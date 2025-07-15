from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.grammer import Grammer


class GrammerRepository(BaseRepository[Grammer]):
    """Repository class for Grammer model.
    これは Grammer Model用の repository 基本(きほん) クラスです。
    """

    def __init__(self, db: Session):
        super().__init__(db, Grammer) 