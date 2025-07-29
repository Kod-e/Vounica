from contextvars import ContextVar
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .uow import UnitOfWork


# 声明一个顶层 ContextVar，以便在整个应用中共享
uow_ctx: ContextVar["UnitOfWork"] = ContextVar("uow_ctx")