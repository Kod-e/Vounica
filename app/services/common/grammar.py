# Grammar service wrapper
from app.services.common.common_base import BaseService
from app.infra.models.grammar import Grammar
from app.infra.repo.grammar_repository import GrammarRepository
from app.infra.context import uow_ctx


class GrammarService(BaseService[Grammar]):
    """Service for Grammar entity."""

    def __init__(self):
        self._uow = uow_ctx.get()
        self._repo: GrammarRepository = GrammarRepository(db=self._uow.db)
        super().__init__(self._repo)

    # 获取用户有多少个记录的grammar, 必须传递language
    async def get_user_grammar_count_prompt_for_agent(self) -> str:
        """Get the user's grammar count."""
        count = await self._repo.get_user_grammar_count(
            user_id=self._uow.current_user.id,
            language=self._uow.target_language
        )
        result_str = f"##User has {count} grammars\n"
        return result_str

__all__ = ["GrammarService"] 