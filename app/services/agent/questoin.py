"""
Question agent module for language learning platform.
This file is redirecting to the new module structure.

言語学習プラットフォームのための質問生成agentモジュールです。
このファイルは新しいモジュール構造にリダイレクトします。
"""

# This file exists for backward compatibility
# Import the implementation from the new module structure
from app.services.agent.question.agent import QuestionAgent

# Re-export
__all__ = ["QuestionAgent"]