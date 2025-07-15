from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.story import Story


class StoryRepository(BaseRepository[Story]):
    """Repository class for Story model.
    これは Story Model用の repository 基本(きほん) クラスです。
    """

    def __init__(self, db: Session):
        super().__init__(db, Story) 