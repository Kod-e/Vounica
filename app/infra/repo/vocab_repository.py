from app.core.db.repository import Repository
from ..models import Vocab
from sqlalchemy.ext.asyncio import AsyncSession


class VocabRepository(Repository[Vocab]):
    """Repository class for Vocab model.
    これは Vocab model用(よう)の repository 基本(きほん) classです。
    """

    def __init__(self, db: AsyncSession):
        super().__init__(Vocab)
        self.db = db 