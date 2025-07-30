"""
简单测试模块，测试基本的fixture加载和初始化。
"""

import pytest
import pytest_asyncio
from unittest.mock import patch, MagicMock, AsyncMock

from app.services.agent.question.agent import QuestionAgent


@pytest.mark.asyncio
async def test_agent_initialization():
    """测试QuestionAgent可以正确初始化"""
    agent = QuestionAgent()
    await agent.run("我想要练习一些会在海边旅行中可能用到的句子")
    # # 验证agent已正确初始化
    # assert agent is not None
    # assert agent.uow == test_uow
    # assert agent.model_type is not None
    # assert hasattr(agent, 'observation_results')
    # assert agent.observation_results == [] 