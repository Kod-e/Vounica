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
    
    # 添加一个grammar, 并且记录一次正确/错误
    async def add_and_record_grammar(self, name: str, usage: str, correct: bool) -> Grammar:
        grammar: Grammar = await self.create({"name": name, "usage": usage, "language": self._uow.target_language})
        await self.record_grammar(grammar.id, correct)
        return grammar
    
    # 记录一次正确/错误
    async def record_grammar(self, grammar_id: int, correct: bool) -> Grammar:
        grammar: Grammar = await self._repo.get_by_id(self._uow.db, grammar_id)
        if grammar is None:
            return f"grammar not found: {grammar_id}"

        cap = 5  # 计算用的有效样本上限

        r = float(grammar.correct_rate or 1.0)  # 约定：n=0 时显示为 1.0
        n = int(grammar.review_count or 0)

        x = 1.0 if correct else 0.0
        n_new = n + 1
        d = min(n_new, cap)  # 计算中的“有效 n”

        # 增量均值（n<cap 时等价于普通平均；n>=cap 后步长固定为 1/cap）
        r_new = r + (x - r) / d

        # 数值安全带（可选）
        if r_new < 0.0: r_new = 0.0
        if r_new > 1.0: r_new = 1.0
        grammar.correct_rate = r_new
        grammar.review_count = n_new
        return grammar  

__all__ = ["GrammarService"] 