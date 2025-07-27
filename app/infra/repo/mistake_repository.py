from app.core.db.repository import Repository
from ..models import Mistake
from sqlalchemy.ext.asyncio import AsyncSession


class MistakeRepository(Repository[Mistake]):
    """Repository class for Mistake model.
    これは Mistake model用(よう)の repository 基本(きほん) classです。
    """

    def __init__(self, db: AsyncSession):
        super().__init__(Mistake)
        self.db = db 