"""
向量存储库模块

这个模块提供了用于向量化和搜索错误原因、语法用法和词汇用法的存储库类。

Vector repository module.
This module provides repository classes for vectorizing and searching mistake error reasons,
grammar usages, and vocabulary usages.

Vector repository module。
このmoduleは、間違いの理由、文法の使用例、語彙の使用例を vectorに変換して検索するための
repositoryクラスを提供します。
"""

from app.core.vector.mistake import MistakeVectorRepository
from app.core.vector.grammar import GrammarVectorRepository
from app.core.vector.vocab import VocabVectorRepository

# 导出所有向量存储库类，使它们可以直接从包中导入
# Export all vector repository classes so they can be imported directly from the package
__all__ = ["MistakeVectorRepository", "GrammarVectorRepository", "VocabVectorRepository"] 