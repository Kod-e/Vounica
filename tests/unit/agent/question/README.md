# QuestionAgent 测试指南

本目录包含了针对 `QuestionAgent` 的单元测试，重点测试了以下几个方面：

1. 基本功能和OPAR循环 (`test_agent_basic.py`)
2. 函数调用功能 (`test_agent_function_calling.py`)
3. 用户记忆对生成问题的影响 (`test_agent_memories.py`)
4. 使用Docker环境的集成测试 (`test_question_agent_docker.py` - 位于 `tests/unit/ai/` 目录)

## 测试环境准备

### 安装依赖

测试需要以下依赖：

```bash
pip install pytest pytest-asyncio fakeredis aiosqlite
```

### 测试数据准备

测试使用内存数据库（SQLite）和内存Redis（fakeredis），不需要额外的数据库设置。

## 运行测试

### 运行所有测试

```bash
# 从项目根目录运行
pytest tests/unit/agent/question -v
```

### 运行特定测试文件

```bash
# 运行基本功能测试
pytest tests/unit/agent/question/test_agent_basic.py -v

# 运行函数调用测试
pytest tests/unit/agent/question/test_agent_function_calling.py -v

# 运行记忆影响测试
pytest tests/unit/agent/question/test_agent_memories.py -v
```

### 运行Docker环境测试

```bash
# 需要Docker环境
pytest tests/unit/ai/test_question_agent_docker.py -v
```

## 测试框架说明

### 测试fixtures

测试使用了以下主要fixtures：

1. **数据库fixtures**:
   - `sqlite_engine` - SQLite内存数据库引擎
   - `async_db_session` - 异步数据库会话

2. **模拟服务fixtures**:
   - `mock_vector_session` - 模拟向量数据库会话
   - `redis_client` - 内存Redis客户端
   - `mock_chat_completion` - 模拟LLM响应

3. **数据准备fixtures**:
   - `test_user` - 测试用户
   - `setup_vocab_data` - 预设词汇数据
   - `setup_memory_data` - 预设记忆数据
   - `setup_mistake_data` - 预设错题数据

4. **综合环境fixtures**:
   - `test_uow` - 完整的测试UnitOfWork
   - `uow_with_custom_memories` - 可自定义记忆的UoW工厂

### 测试模拟策略

1. **LLM模拟**: 使用`mock_chat_completion_factory`生成可配置的模拟响应
2. **数据库**: 使用SQLite内存数据库
3. **Redis**: 使用fakeredis提供的内存Redis服务
4. **向量搜索**: 模拟向量搜索结果

## 测试覆盖范围

- **OPAR循环**: 测试完整的观察、计划、行动、反思循环
- **函数调用处理**: 测试函数调用的正确解析和处理
- **错误处理**: 测试函数调用错误和参数错误的情况
- **记忆与个性化**: 测试不同用户记忆如何影响问题生成
- **配额管理**: 测试Token配额的检查和消费

## 注意事项

1. 所有测试fixtures的scope都是"function"，确保测试之间的隔离
2. Docker测试需要docker-compose.test.yml文件和Docker环境
3. 测试模拟了不同用户场景（动漫爱好者、商务人士、旅行者） 