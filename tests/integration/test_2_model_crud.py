# 集成测试 - 模型CRUD操作
# 测试Grammar, Mistake, Story和Vocab模型的CRUD功能
import pytest
from datetime import datetime

# 测试顺序标记，确保在认证测试之后运行
pytestmark = [pytest.mark.order(5)]


# ----------------------------------------------------------------------------
# Grammar CRUD测试
# ----------------------------------------------------------------------------

@pytest.fixture(scope="module")
def grammar_data():
    # 测试用Grammar数据
    return {
        "name": "the name of grammar",
        "usage": "the usage of grammar",
        "status": 0.75,
        "language": "ja"
    }


def test_grammar_create(authenticated_client, grammar_data):
    # 测试创建Grammar记录
    response = authenticated_client.post(
        "/v1/grammar/create",
        json=grammar_data
    )
    assert response.status_code == 200, f"Failed to create grammar: {response.text}"
    data = response.json()
    
    # 验证返回数据
    assert "id" in data, "No id in response"
    assert data["name"] == grammar_data["name"]
    assert data["usage"] == grammar_data["usage"]
    assert data["status"] == grammar_data["status"]
    assert data["language"] == grammar_data["language"]
    assert "created_at" in data
    assert "updated_at" in data
    
    # 将创建的ID保存在module级别，供后续测试使用
    pytest.grammar_id = data["id"]


def test_grammar_get_page(authenticated_client):
    # 测试获取Grammar分页列表
    response = authenticated_client.get("/v1/grammar/page?limit=10&offset=0")
    assert response.status_code == 200, f"Failed to get grammar list: {response.text}"
    data = response.json()
    
    # 验证返回的是列表且不为空
    assert isinstance(data, list), "Response is not a list"
    assert len(data) > 0, "Grammar list is empty"
    
    # 验证第一条数据包含预期字段
    first_item = data[0]
    assert "id" in first_item
    assert "name" in first_item
    assert "usage" in first_item
    assert "status" in first_item
    assert "language" in first_item
    assert "created_at" in first_item
    assert "updated_at" in first_item


def test_grammar_update(authenticated_client, grammar_data):
    # 测试更新Grammar记录
    # 确保前面的测试已设置grammar_id
    assert hasattr(pytest, "grammar_id"), "Grammar ID not set by previous test"
    
    # 准备更新数据
    update_data = grammar_data.copy()
    update_data["id"] = pytest.grammar_id
    update_data["status"] = 0.85
    update_data["usage"] = "updated usage of grammar"
    
    # 执行更新
    response = authenticated_client.post(
        "/v1/grammar/update",
        json=update_data
    )
    assert response.status_code == 200, f"Failed to update grammar: {response.text}"
    data = response.json()
    
    # 验证数据已更新
    assert data["id"] == pytest.grammar_id
    assert data["status"] == 0.85
    assert data["usage"] == "updated usage of grammar"


def test_grammar_delete(authenticated_client):
    # 测试删除Grammar记录
    # 确保前面的测试已设置grammar_id
    assert hasattr(pytest, "grammar_id"), "Grammar ID not set by previous test"
    
    # 执行删除
    response = authenticated_client.delete(
        f"/v1/grammar/delete?grammar_id={pytest.grammar_id}"
    )
    assert response.status_code == 200, f"Failed to delete grammar: {response.text}"
    data = response.json()
    
    # 验证返回的是被删除的记录
    assert data["id"] == pytest.grammar_id


# ----------------------------------------------------------------------------
# Mistake CRUD测试
# ----------------------------------------------------------------------------

@pytest.fixture(scope="module")
def mistake_data():
    # 测试用Mistake数据
    return {
        "question": "test question",
        "question_type": "test_type",
        "language": "ja",
        "answer": "wrong answer",
        "correct_answer": "right answer",
        "error_reason": "explanation of error"
    }


def test_mistake_create(authenticated_client, mistake_data):
    # 测试创建Mistake记录
    response = authenticated_client.post(
        "/v1/mistake/create",
        json=mistake_data
    )
    assert response.status_code == 200, f"Failed to create mistake: {response.text}"
    data = response.json()
    
    # 验证返回数据
    assert "id" in data, "No id in response"
    assert data["question"] == mistake_data["question"]
    assert data["question_type"] == mistake_data["question_type"]
    assert data["language"] == mistake_data["language"]
    assert data["answer"] == mistake_data["answer"]
    assert data["correct_answer"] == mistake_data["correct_answer"]
    assert data["error_reason"] == mistake_data["error_reason"]
    assert "created_at" in data
    assert "updated_at" in data
    
    # 将创建的ID保存在module级别，供后续测试使用
    pytest.mistake_id = data["id"]


def test_mistake_get_page(authenticated_client):
    # 测试获取Mistake分页列表
    response = authenticated_client.get("/v1/mistake/page?limit=10&offset=0")
    assert response.status_code == 200, f"Failed to get mistake list: {response.text}"
    data = response.json()
    
    # 验证返回的是列表且不为空
    assert isinstance(data, list), "Response is not a list"
    assert len(data) > 0, "Mistake list is empty"


def test_mistake_get_recent(authenticated_client):
    # 测试获取用户最近错题
    response = authenticated_client.get("/v1/mistake/recent?limit=5&offset=0")
    assert response.status_code == 200, f"Failed to get recent mistakes: {response.text}"
    data = response.json()
    
    # 验证返回的是列表
    assert isinstance(data, list), "Response is not a list"


def test_mistake_update(authenticated_client, mistake_data):
    # 测试更新Mistake记录
    # 确保前面的测试已设置mistake_id
    assert hasattr(pytest, "mistake_id"), "Mistake ID not set by previous test"
    
    # 准备更新数据
    update_data = mistake_data.copy()
    update_data["id"] = pytest.mistake_id
    update_data["error_reason"] = "updated explanation"
    
    # 执行更新
    response = authenticated_client.post(
        "/v1/mistake/update",
        json=update_data
    )
    assert response.status_code == 200, f"Failed to update mistake: {response.text}"
    data = response.json()
    
    # 验证数据已更新
    assert data["id"] == pytest.mistake_id
    assert data["error_reason"] == update_data["error_reason"]


def test_mistake_delete(authenticated_client):
    # 测试删除Mistake记录
    # 确保前面的测试已设置mistake_id
    assert hasattr(pytest, "mistake_id"), "Mistake ID not set by previous test"
    
    # 执行删除
    response = authenticated_client.delete(
        f"/v1/mistake/delete?mistake_id={pytest.mistake_id}"
    )
    assert response.status_code == 200, f"Failed to delete mistake: {response.text}"
    data = response.json()
    
    # 验证返回的是被删除的记录
    assert data["id"] == pytest.mistake_id


# ----------------------------------------------------------------------------
# Story CRUD测试
# ----------------------------------------------------------------------------

@pytest.fixture(scope="module")
def story_data():
    # 测试用Story数据
    return {
        "content": "test content of story",
        "summary": "test summary of story",
        "category": "test category",
        "language": "ja"
    }


def test_story_create(authenticated_client, story_data):
    # 测试创建Story记录
    response = authenticated_client.post(
        "/v1/story/create",
        json=story_data
    )
    assert response.status_code == 200, f"Failed to create story: {response.text}"
    data = response.json()
    
    # 验证返回数据
    assert "id" in data, "No id in response"
    assert data["content"] == story_data["content"]
    assert data["summary"] == story_data["summary"]
    assert data["category"] == story_data["category"]
    assert data["language"] == story_data["language"]
    assert "created_at" in data
    assert "updated_at" in data
    
    # 将创建的ID保存在module级别，供后续测试使用
    pytest.story_id = data["id"]


def test_story_get_page(authenticated_client):
    # 测试获取Story分页列表
    response = authenticated_client.get("/v1/story/page?limit=10&offset=0")
    assert response.status_code == 200, f"Failed to get story list: {response.text}"
    data = response.json()
    
    # 验证返回的是列表且不为空
    assert isinstance(data, list), "Response is not a list"
    assert len(data) > 0, "Story list is empty"


def test_story_update(authenticated_client, story_data):
    # 测试更新Story记录
    # 确保前面的测试已设置story_id
    assert hasattr(pytest, "story_id"), "Story ID not set by previous test"
    
    # 准备更新数据
    update_data = story_data.copy()
    update_data["id"] = pytest.story_id
    update_data["summary"] = "updated summary"
    
    # 执行更新
    response = authenticated_client.post(
        "/v1/story/update",
        json=update_data
    )
    assert response.status_code == 200, f"Failed to update story: {response.text}"
    data = response.json()
    
    # 验证数据已更新
    assert data["id"] == pytest.story_id
    assert data["summary"] == update_data["summary"]


def test_story_delete(authenticated_client):
    # 测试删除Story记录
    # 确保前面的测试已设置story_id
    assert hasattr(pytest, "story_id"), "Story ID not set by previous test"
    
    # 执行删除
    response = authenticated_client.delete(
        f"/v1/story/delete?story_id={pytest.story_id}"
    )
    assert response.status_code == 200, f"Failed to delete story: {response.text}"
    data = response.json()
    
    # 验证返回的是被删除的记录
    assert data["id"] == pytest.story_id


# ----------------------------------------------------------------------------
# Vocab CRUD测试
# ----------------------------------------------------------------------------

@pytest.fixture(scope="module")
def vocab_data():
    # 测试用Vocab数据
    return {
        "name": "test vocabulary",
        "usage": "example usage of vocabulary",
        "status": 0.6,
        "language": "ja"
    }


def test_vocab_create(authenticated_client, vocab_data):
    # 测试创建Vocab记录
    response = authenticated_client.post(
        "/v1/vocab/create",
        json=vocab_data
    )
    assert response.status_code == 200, f"Failed to create vocab: {response.text}"
    data = response.json()
    
    # 验证返回数据
    assert "id" in data, "No id in response"
    assert data["name"] == vocab_data["name"]
    assert data["usage"] == vocab_data["usage"]
    assert data["status"] == vocab_data["status"]
    assert data["language"] == vocab_data["language"]
    assert "created_at" in data
    assert "updated_at" in data
    
    # 将创建的ID保存在module级别，供后续测试使用
    pytest.vocab_id = data["id"]


def test_vocab_get_page(authenticated_client):
    # 测试获取Vocab分页列表
    response = authenticated_client.get("/v1/vocab/page?limit=10&offset=0")
    assert response.status_code == 200, f"Failed to get vocab list: {response.text}"
    data = response.json()
    
    # 验证返回的是列表且不为空
    assert isinstance(data, list), "Response is not a list"
    assert len(data) > 0, "Vocab list is empty"


def test_vocab_update(authenticated_client, vocab_data):
    # 测试更新Vocab记录
    # 确保前面的测试已设置vocab_id
    assert hasattr(pytest, "vocab_id"), "Vocab ID not set by previous test"
    
    # 准备更新数据
    update_data = vocab_data.copy()
    update_data["id"] = pytest.vocab_id
    update_data["usage"] = "updated example usage"
    update_data["status"] = 0.8
    
    # 执行更新
    response = authenticated_client.post(
        "/v1/vocab/update",
        json=update_data
    )
    assert response.status_code == 200, f"Failed to update vocab: {response.text}"
    data = response.json()
    
    # 验证数据已更新
    assert data["id"] == pytest.vocab_id
    assert data["usage"] == update_data["usage"]
    assert data["status"] == update_data["status"]


def test_vocab_delete(authenticated_client):
    # 测试删除Vocab记录
    # 确保前面的测试已设置vocab_id
    assert hasattr(pytest, "vocab_id"), "Vocab ID not set by previous test"
    
    # 执行删除
    response = authenticated_client.delete(
        f"/v1/vocab/delete?vocab_id={pytest.vocab_id}"
    )
    assert response.status_code == 200, f"Failed to delete vocab: {response.text}"
    data = response.json()
    
    # 验证返回的是被删除的记录
    assert data["id"] == pytest.vocab_id 