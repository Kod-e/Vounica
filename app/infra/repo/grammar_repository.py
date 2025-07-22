from app.core.db.repository import Repository
from ..models import Grammar

class GrammarRepository(Repository[Grammar]):
    """Repository class for Grammar model.
    これは Grammar model用(よう)の repository 基本(きほん) classです。
    """

    def __init__(self):
        super().__init__(Grammar) 