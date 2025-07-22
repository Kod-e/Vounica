from types import SimpleNamespace
from app.services.tools.search import search_resource, ResourceLiteral
import pytest


class _EmptyScalarResult:
    """Mock SQLAlchemy result that returns empty list."""

    def scalars(self):  # noqa: D401
        return self

    def all(self):  # noqa: D401
        return []


class _DummySession:
    async def execute(self, _stmt):  # noqa: D401
        return _EmptyScalarResult()


@pytest.mark.asyncio
async def test_search_resource_regex_empty():
    """When no record matches, search_resource should return empty list."""

    uow = SimpleNamespace(user_id=123, db=_DummySession())

    result = await search_resource(
        uow,
        resource="vocab",  # type: ignore[arg-type]
        field="name",
        method="regex",
        query="nonexistent",
        limit=5,
    )

    assert result == []


@pytest.mark.asyncio
async def test_search_resource_invalid_field():
    """Unsupported field should raise ValueError."""

    uow = SimpleNamespace(user_id=123, db=_DummySession())

    with pytest.raises(ValueError):
        await search_resource(
            uow,
            resource="vocab",  # type: ignore[arg-type]
            field="invalid_field",
            method="regex",
            query="x",
        )