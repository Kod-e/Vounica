from app.infra.models.memory import Memory
from app.services.common.memory import MemoryService
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

async def add_memory(
    category: str,
    content: str,
    summary: str,
    priority: int = 0,
) -> str:
    session = uow_ctx.get().db
    async with _lock_for_session(session):
        memory: Memory = await MemoryService().create({"category": category, "content": content, "summary": summary, "language": uow_ctx.get().target_language, "priority": priority})
    return f"""
memory added:
id: {memory.id}
summary: {summary}
category: {category}
content: {content}
priority: {priority}
updated_at: {memory.updated_at.isoformat()}
"""


async def update_memory(memory_id: int, category: str, content: str, summary: str, priority: int = 0) -> str:
    session = uow_ctx.get().db
    async with _lock_for_session(session):
        memory: Memory = await MemoryService().update({"id": memory_id, "category": category, "content": content, "summary": summary, "language": uow_ctx.get().target_language, "priority": priority})
    return f"""
memory updated:
id: {memory.id}
summary: {summary}
category: {category}
content: {content}
priority: {priority}
updated_at: {memory.updated_at.isoformat()}
"""

async def delete_memory(memory_id: int) -> str:
    session = uow_ctx.get().db
    async with _lock_for_session(session):
        await MemoryService().delete(memory_id)
    return f"""
memory deleted:
id: {memory_id}
"""