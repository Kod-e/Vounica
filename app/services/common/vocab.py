"""Vocab service wrapper."""

from typing import List
from app.services.common.common_base import BaseService
from app.infra.models.vocab import Vocab
from app.infra.repo.vocab_repository import VocabRepository
from app.infra.context import uow_ctx


class VocabService(BaseService[Vocab]):
    """Service for Vocab entity."""

    def __init__(self):
        self._uow = uow_ctx.get()
        self._repo : VocabRepository = VocabRepository(db=self._uow.db)
        super().__init__(self._repo)

    # 获取list, 带分割
    async def get_user_vocabs(self, offset: int = 0, limit: int = 100) -> List[Vocab]:
        """Get the list of vocabs with split."""
        return await self._repo.get_user_vocabs(
            user_id=self._uow.current_user.id,
            offset=offset,
            limit=limit,
            language=self._uow.target_language
        )
    # 获取user有多少个记录的vocab, 返回Prompt
    async def get_user_vocab_count_prompt_for_agent(self) -> str:
        """Get the user's vocab count prompt for agent."""
        count = await self._repo.get_user_vocab_count(
            user_id=self._uow.current_user.id,
            language=self._uow.target_language
        )
        result_str = f"##User has {count} vocabs\n"
        return result_str
    
    # 添加一个vocab, 并且记录一次正确/错误
    async def add_and_record_vocab(self, name: str, usage: str, correct: bool) -> Vocab:
        vocab: Vocab = await self.create({"name": name, "usage": usage, "language": self._uow.target_language})
        await self.record_vocab(vocab.id, correct)
        return vocab
    
    # 记录一次正确/错误
    async def record_vocab(self, vocab_id: int, correct: bool) -> Vocab:
        vocab: Vocab = await self._repo.get_by_id(self._uow.db, vocab_id)
        if vocab is None:
            return f"vocab not found: {vocab_id}"

        cap = 5  # 计算用的有效样本上限

        r = float(vocab.correct_rate or 1.0)  # 约定：n=0 时显示为 1.0
        n = int(vocab.review_count or 0)

        x = 1.0 if correct else 0.0
        n_new = n + 1
        d = min(n_new, cap)  # 计算中的“有效 n”

        # 增量均值（n<cap 时等价于普通平均；n>=cap 后步长固定为 1/cap）
        r_new = r + (x - r) / d

        # 数值安全带（可选）
        if r_new < 0.0: r_new = 0.0
        if r_new > 1.0: r_new = 1.0
        vocab.correct_rate = r_new
        vocab.review_count = n_new
        return vocab
    
    # 获取最近的5条vocab的prompt
    async def get_recent_vocab_prompt_for_agent(self, limit: int = 5) -> str:
        """Get the recent vocab prompt for agent."""
        vocabs: List[Vocab] = await self._repo.get_recent_records(
            db=self._uow.db,
            filter={"user_id": self._uow.current_user.id, "language": self._uow.target_language},
            limit=limit
        )
        result_str = "#User's Last 5 Recent Vocabs\n"
        result_str += f"ID|Time|Name|Usage|Status(Total Correct Rate in last 5 times, max 1.0, min 0.0)\n"
        if len(vocabs) == 0:
            result_str += "No Any vocab Record\n"
            return result_str
        for vocab in vocabs:
            result_str += f"{vocab.id}|{vocab.updated_at.strftime('%Y-%m-%d')}|{vocab.name}|{vocab.usage}|{vocab.status:.2f}\n"
        return result_str
    
__all__ = ["VocabService"] 