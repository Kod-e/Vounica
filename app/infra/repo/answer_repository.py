from app.core.db.repository import Repository
from ..models import Answer
    

class AnswerRepository(Repository[Answer]):
    """Repository class for Answer model.djbbbf
    これは Answer model用(よう)の repository 基本(きほん) classです。
    """

    def __init__(self):
        super().__init__(Answer) 