"""Memory service wrapper."""

from app.services.common.common_base import BaseService
from app.infra.models.memory import Memory
from app.infra.repo.memory_repository import MemoryRepository


class MemoryService(BaseService[Memory]):
    """Service for Memory entity."""

    def __init__(self):
        super().__init__(MemoryRepository())


__all__ = ["MemoryService"] 