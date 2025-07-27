import pytest
from unittest.mock import patch, MagicMock

from app.services.agent.question.agent import QuestionAgent


@pytest.mark.asyncio
async def test_question_agent_with_mock_uow(mock_uow, mock_search_resource):
    """
    Test QuestionAgent with real LLM response but mocked search.
    
    mockされた検索と実際のLLMを使ってQuestionAgentをテストします。
    """
    # 添加user属性指向current_user以匹配QuestionAgent的期望
    setattr(mock_uow, 'user', mock_uow.current_user)
    
    # 只patch search_resource，不patch chat_completion
    with patch('app.services.agent.question.agent.search_resource', mock_search_resource):
        
        # Create agent with mocked UoW
        agent = QuestionAgent(uow=mock_uow)
        
        # Run the agent with a test query
        result = await agent.run("I want to learn English")
        
        # 输出实际LLM响应，便于观察
        print("LLM generated questions:")
        for i, question in enumerate(result.get("questions", [])):
            print(f"Question {i+1}: {question.get('question_text', '')}")
            print(f"Answer: {question.get('correct_answer', '')}")
            print("-" * 40)
        
        # Validate basic structure of result
        assert isinstance(result, dict)
        assert "questions" in result
        assert "is_valid" in result
        assert "context" in result


@pytest.mark.asyncio
async def test_question_agent_new_user(new_user_uow, mock_search_resource):
    """
    Test QuestionAgent with a new user and real LLM.
    
    新しいユーザーと実際のLLMでQuestionAgentをテストします。
    """
    # 添加user属性指向current_user以匹配QuestionAgent的期望
    setattr(new_user_uow, 'user', new_user_uow.current_user)
    
    # Configure search_resource to return empty results (simulating new user)
    mock_search_resource.return_value = []
    
    # 只patch search_resource，不patch chat_completion
    with patch('app.services.agent.question.agent.search_resource', mock_search_resource):
        
        # Create agent with new user UoW
        agent = QuestionAgent(uow=new_user_uow)
        
        # Run the agent
        result = await agent.run("I want to learn basic Japanese")
        
        # 输出实际LLM响应，便于观察
        print("LLM generated questions for new user:")
        for i, question in enumerate(result.get("questions", [])):
            print(f"Question {i+1}: {question.get('question_text', '')}")
            print(f"Answer: {question.get('correct_answer', '')}")
            print("-" * 40)
        
        # Verify that agent recognized this as a new user
        assert result["context"]["user_is_new"] is True