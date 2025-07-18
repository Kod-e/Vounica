# 移除同步 Session, 使用通用异步 Repository
from app.core.db.repository import Repository
from app.models.story import Story


class StoryRepository(Repository[Story]):
    """Repository class for Story model.
    これは Story model用(よう)の repository 基本(きほん) classです。
    """

    def __init__(self):
        super().__init__(Story) 