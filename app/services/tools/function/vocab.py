from app.infra.models.vocab import Vocab
from app.services.common.vocab import VocabService
from app.infra.context import uow_ctx
import asyncio
import weakref
from sqlalchemy.ext.asyncio import AsyncSession

# 针对会话级串行化，避免同一 AsyncSession 在并发下重入 flush
_session_locks = weakref.WeakKeyDictionary()

def _lock_for_session(session: AsyncSession) -> asyncio.Lock:
    lock = _session_locks.get(session)
    if lock is None:
        lock = asyncio.Lock()
        _session_locks[session] = lock
    return lock

async def add_vocab(
    name: str,
    usage: str,
) -> str:
    session = uow_ctx.get().db
    async with _lock_for_session(session):
        vocab: Vocab = await VocabService().create({"name": name, "usage": usage, "language": uow_ctx.get().target_language})
    return f"""
vocab added:
id: {vocab.id}
name: {name}
usage: {usage}
language: {uow_ctx.get().target_language}
updated_at: {vocab.updated_at.isoformat()}
"""

async def add_and_record_vocab(name: str, usage: str, correct: bool) -> Vocab:
    session = uow_ctx.get().db
    async with _lock_for_session(session):
        vocab =  await VocabService().add_and_record_vocab(name, usage, correct)
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
    session = uow_ctx.get().db
    async with _lock_for_session(session):
        vocab: Vocab = await VocabService().record_vocab(vocab_id, correct)
    return f"""
vocab recorded:
id: {vocab.id}
correct: {correct}
updated_at: {vocab.updated_at.isoformat()}
"""