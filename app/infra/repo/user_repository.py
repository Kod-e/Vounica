from app.core.db.repository import Repository
from ..models import User


class UserRepository(Repository[User]):
    """
    Repository class for User model.
    これは User model用(よう)の repository 基本(きほん) classです。
    """

    def __init__(self):
        # 初始化时仅传入模型类，Session 由具体调用方法时注入
        super().__init__(User) 