"""
简单测试模块，测试基本的fixture加载和初始化。
"""

import pytest
import pytest_asyncio
from unittest.mock import patch, MagicMock, AsyncMock

from app.services.agent.question.agent import QuestionAgent


@pytest.mark.asyncio
async def test_agent_initialization(test_uow):
    """测试QuestionAgent可以正确初始化"""
    agent = QuestionAgent(uow=test_uow)
    await agent.run("生成10个问题, 大致的测试我的日语水平")
    # 验证agent已正确初始化
    assert agent is not None
    assert agent.uow == test_uow
    assert agent.model_type is not None
    assert hasattr(agent, 'observation_results')
    assert agent.observation_results == [] 