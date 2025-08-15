from app.infra.models.vocab import Vocab
from app.services.common.vocab import VocabService
from app.infra.context import uow_ctx

async def add_vocab(
    name: str,
    usage: str,
) -> str:
    vocab: Vocab = await VocabService().create({"name": name, "usage": usage, "language": uow_ctx.get().target_language})
    return f"""
vocab added:
id: {vocab.id}
name: {name}
usage: {usage}
language: {uow_ctx.get().target_language}
updated_at: {vocab.updated_at.isoformat()}
"""

# 给Vocab记录一次correct/incorrect
async def record_vocab(vocab_id: int,correct: bool) -> str:
    vocab: Vocab = await VocabService().record_vocab(vocab_id, correct)
    return f"""
vocab recorded:
id: {vocab.id}
correct: {correct}
updated_at: {vocab.updated_at.isoformat()}
"""