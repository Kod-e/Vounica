# 移除同步 Session, 使用通用异步 Repository
from app.core.db.repository import Repository
from app.models.mistake import Mistake


class MistakeRepository(Repository[Mistake]):
    """Repository class for Mistake model.
    これは Mistake model用(よう)の repository 基本(きほん) classです。
    """

    def __init__(self):
        super().__init__(Mistake) 