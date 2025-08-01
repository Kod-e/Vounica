from app.infra.models.memory import Memory
from app.services.common.memory import MemoryService

async def add_memory(
    category: str,
    content: str,
    priority: int = 0,
) -> str:
    memory: Memory = await MemoryService.create({"category": category, "content": content, "priority": priority})
    return f"""
memory added:
id: {memory.id}
category: {category}
content: {content}
priority: {priority}
updated_at: {memory.updated_at.isoformat()}
"""


async def update_memory(memory_id: int, category: str, content: str, priority: int = 0) -> str:
    memory: Memory = await MemoryService.update({"id": memory_id, "category": category, "content": content, "priority": priority})
    return f"""
memory updated:
id: {memory.id}
category: {category}
content: {content}
priority: {priority}
updated_at: {memory.updated_at.isoformat()}
"""

async def delete_memory(memory_id: int) -> str:
    await MemoryService.delete(memory_id)
    return f"""
memory deleted:
id: {memory_id}
"""