import pytest
import pytest_asyncio
from app.infra.schemas import (
    GrammarCreateSchema,
    GrammarUpdateSchema,
    MemoryCreateSchema,
    MemoryUpdateSchema,
    MistakeCreateSchema,
    MistakeSchema,
    StoryCreateSchema,
    StorySchema,
    VocabCreateSchema,
    VocabSchema,
)

@pytest.mark.order(1)
@pytest.mark.asyncio
async def test_grammar_crud(authenticated_async_client):
    # 第1步：创建Grammar
    response = await authenticated_async_client.post(
        "/v1/grammar/create",
        json=GrammarCreateSchema(
            name="the name of grammar",
            usage="the usage of grammar",
            status=0.75,
            language="ja"
        ).model_dump()
    )
    assert response.status_code == 200, f"Failed to create grammar: {response.text}"
    created_data = response.json()
    
    # 验证返回数据
    assert "id" in created_data, "No id in response"
    assert created_data["name"] == "the name of grammar"
    assert created_data["usage"] == "the usage of grammar"
    assert created_data["status"] == 0.75
    assert created_data["language"] == "ja"
    assert "created_at" in created_data
    assert "updated_at" in created_data
    
    # 保存ID用于后续操作
    grammar_id = created_data["id"]
    
    # 第2步：获取Grammar列表 (不验证长度，因为可能存在权限过滤)
    response = await authenticated_async_client.get("/v1/grammar/page?limit=10&offset=0")
    assert response.status_code == 200, f"Failed to get grammar list: {response.text}"
    data = response.json()
    
    # 验证返回的是列表
    assert isinstance(data, list), "Response is not a list"
    # 注意：列表可能为空，这取决于权限过滤，所以不验证长度
    
    # 第3步：更新Grammar
    response = await authenticated_async_client.post(
        "/v1/grammar/update",
        json=GrammarUpdateSchema(
            id=grammar_id,
            status=0.85,
            usage="updated usage of grammar",
            name=created_data["name"]
        ).model_dump()
    )
    assert response.status_code == 200, f"Failed to update grammar: {response.text}"
    data = response.json()
    
    # 验证数据已更新
    assert data["id"] == grammar_id
    assert data["status"] == 0.85
    assert data["usage"] == "updated usage of grammar"
    
    # 第4步：删除Grammar
    response = await authenticated_async_client.delete(
        f"/v1/grammar/delete?grammar_id={grammar_id}"
    )
    assert response.status_code == 200, f"Failed to delete grammar: {response.text}"
    data = response.json()
    
    # 验证返回的是被删除的记录
    assert data["id"] == grammar_id

@pytest.mark.order(2)
@pytest.mark.asyncio
async def test_memory_crud(authenticated_async_client):
    # Step 1: Create Memory
    response = await authenticated_async_client.post(
        "/v1/memory/create",
        json=MemoryCreateSchema(
            content="memory content",
            category="life",
            priority=3,
            language="ja",
        ).model_dump(),
    )
    assert response.status_code == 200, f"Failed to create memory: {response.text}"
    created_data = response.json()

    # Validate response
    assert "id" in created_data, "No id in response"
    assert created_data["content"] == "memory content"
    assert created_data["category"] == "life"
    assert created_data["priority"] == 3
    assert created_data["language"] == "ja"

    memory_id = created_data["id"]

    # Step 2: List Memory
    response = await authenticated_async_client.get("/v1/memory/page?limit=10&offset=0")
    assert response.status_code == 200, f"Failed to get memory list: {response.text}"
    data = response.json()
    assert isinstance(data, list), "Response is not a list"

    # Step 3: Update Memory
    response = await authenticated_async_client.post(
        "/v1/memory/update",
        json=MemoryUpdateSchema(
            id=memory_id,
            content="updated memory content",
            priority=4,
        ).model_dump(),
    )
    assert response.status_code == 200, f"Failed to update memory: {response.text}"
    data = response.json()
    assert data["id"] == memory_id
    assert data["content"] == "updated memory content"
    assert data["priority"] == 4

    # Step 4: Delete Memory
    response = await authenticated_async_client.delete(f"/v1/memory/delete?memory_id={memory_id}")
    assert response.status_code == 200, f"Failed to delete memory: {response.text}"
    data = response.json()
    assert data["id"] == memory_id

@pytest.mark.order(3)
@pytest.mark.asyncio
async def test_mistake_crud(authenticated_async_client):
    # Step 1: Create Mistake
    response = await authenticated_async_client.post(
        "/v1/mistake/create",
        json=MistakeCreateSchema(
            question="What is 2+2?",
            question_type="math",
            language="en",
            answer="5",
            correct_answer="4",
            error_reason="addition mistake",
        ).model_dump(),
    )
    assert response.status_code == 200, f"Failed to create mistake: {response.text}"
    created_data = response.json()
    mistake_id = created_data["id"]

    # Step 2: List Mistake
    response = await authenticated_async_client.get("/v1/mistake/page?limit=10&offset=0")
    assert response.status_code == 200, f"Failed to get mistake list: {response.text}"
    data = response.json()
    assert isinstance(data, list), "Response is not a list"

    # Step 3: Update Mistake (need full schema fields)
    updated_payload = created_data.copy()
    updated_payload["answer"] = "4"
    updated_payload["error_reason"] = "fixed"

    response = await authenticated_async_client.post(
        "/v1/mistake/update",
        json=updated_payload,
    )
    assert response.status_code == 200, f"Failed to update mistake: {response.text}"
    data = response.json()
    assert data["id"] == mistake_id
    assert data["answer"] == "4"
    assert data["error_reason"] == "fixed"

    # Step 4: Delete Mistake
    response = await authenticated_async_client.delete(f"/v1/mistake/delete?mistake_id={mistake_id}")
    assert response.status_code == 200, f"Failed to delete mistake: {response.text}"
    data = response.json()
    assert data["id"] == mistake_id

@pytest.mark.order(4)
@pytest.mark.asyncio
async def test_story_crud(authenticated_async_client):
    # Step 1: Create Story
    response = await authenticated_async_client.post(
        "/v1/story/create",
        json=StoryCreateSchema(
            content="Once upon a time...",
            summary="A simple tale",
            category="fiction",
            language="en",
        ).model_dump(),
    )
    assert response.status_code == 200, f"Failed to create story: {response.text}"
    created_data = response.json()
    story_id = created_data["id"]

    # Step 2: List Story
    response = await authenticated_async_client.get("/v1/story/page?limit=10&offset=0")
    assert response.status_code == 200, f"Failed to get story list: {response.text}"
    data = response.json()
    assert isinstance(data, list), "Response is not a list"

    # Step 3: Update Story (full payload)
    updated_payload = created_data.copy()
    updated_payload["summary"] = "An updated tale"

    response = await authenticated_async_client.post(
        "/v1/story/update",
        json=updated_payload,
    )
    assert response.status_code == 200, f"Failed to update story: {response.text}"
    data = response.json()
    assert data["id"] == story_id
    assert data["summary"] == "An updated tale"

    # Step 4: Delete Story
    response = await authenticated_async_client.delete(f"/v1/story/delete?story_id={story_id}")
    assert response.status_code == 200, f"Failed to delete story: {response.text}"
    data = response.json()
    assert data["id"] == story_id

@pytest.mark.order(5)
@pytest.mark.asyncio
async def test_vocab_crud(authenticated_async_client):
    # Step 1: Create Vocab
    response = await authenticated_async_client.post(
        "/v1/vocab/create",
        json=VocabCreateSchema(
            name="単語",
            usage="word usage",
            status=0.25,
            language="ja",
        ).model_dump(),
    )
    assert response.status_code == 200, f"Failed to create vocab: {response.text}"
    created_data = response.json()
    vocab_id = created_data["id"]

    # Step 2: List Vocab
    response = await authenticated_async_client.get("/v1/vocab/page?limit=10&offset=0")
    assert response.status_code == 200, f"Failed to get vocab list: {response.text}"
    data = response.json()
    assert isinstance(data, list), "Response is not a list"

    # Step 3: Update Vocab (full payload)
    updated_payload = created_data.copy()
    updated_payload["status"] = 0.75
    updated_payload["usage"] = "updated usage"

    response = await authenticated_async_client.post(
        "/v1/vocab/update",
        json=updated_payload,
    )
    assert response.status_code == 200, f"Failed to update vocab: {response.text}"
    data = response.json()
    assert data["id"] == vocab_id
    assert data["status"] == 0.75
    assert data["usage"] == "updated usage"

    # Step 4: Delete Vocab
    response = await authenticated_async_client.delete(f"/v1/vocab/delete?vocab_id={vocab_id}")
    assert response.status_code == 200, f"Failed to delete vocab: {response.text}"
    data = response.json()
    assert data["id"] == vocab_id
