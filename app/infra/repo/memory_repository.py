from app.core.db.repository import Repository
from ..models import Memory


class MemoryRepository(Repository[Memory]):
    """Repository class for Memory model.
    これは Memory model用(よう)の repository 基本(きほん) classです。
    """

    def __init__(self):
        super().__init__(Memory) 