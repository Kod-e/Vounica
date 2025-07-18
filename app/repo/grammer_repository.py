# 移除同步 Session, 使用通用异步 Repository
from app.core.db.repository import Repository
from app.models.grammer import Grammer


class GrammerRepository(Repository[Grammer]):
    """Repository class for Grammer model.
    これは Grammer model用(よう)の repository 基本(きほん) classです。
    """

    def __init__(self):
        super().__init__(Grammer) 