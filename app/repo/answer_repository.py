# 移除同步 Session, 使用通用异步 Repository
from app.core.db.repository import Repository
from app.models.answers import Answer


class AnswerRepository(Repository[Answer]):
    """Repository class for Answer model.djbbbf
    これは Answer model用(よう)の repository 基本(きほん) classです。
    """

    def __init__(self):
        super().__init__(Answer) 