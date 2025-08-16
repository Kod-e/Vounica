"""
Assembly question implementation based on QuestionSpec.

选词填空 / 词块拼接实现。
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Literal

from pydantic import Field

from app.services.question.base.spec import JudgeResult, QuestionSpec
from app.services.question.base.registry import register_question_type
from app.services.question.base.types import QuestionType
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.language_models import LanguageModelInput
from app.llm.client import chat_completion
from app.llm.models import LLMModel
from app.infra.context import uow_ctx
import re, unicodedata

@register_question_type(QuestionType.ASSEMBLY)
class AssemblyQuestion(QuestionSpec):
    """
    Assembly question (fill in the blanks).

    選択(せんたく)語(ご)の組(く)み立(た)て問題(もんだい)。
    """
    # 题干及答案相关字段 (Pydantic 模型字段)
    stem: str
    options: List[str]
    correct_answer: List[str]
    # 用户答案
    answer: Optional[List[str]] = None
    question_type: Literal[QuestionType.ASSEMBLY] = Field(
        default=QuestionType.ASSEMBLY, description="discriminator"
    )

    # 描述题目
    def prompt(self) -> str:
        """Return the question stem as prompt."""
        question_prompt = f"""
Assembly Question:
{self.stem}
Options:
{self.options}
Correct Answer:
{self.correct_answer}
        """
        return question_prompt

    def _normalize_tokens(self, tokens: List[str]) -> str:
        """Normalize tokens for lenient comparison (NFKC, lowercase, strip punctuation)."""
        text = " ".join(tokens)
        text = unicodedata.normalize("NFKC", text).lower()
        text = re.sub(r"[“”\"‘’'`]", "", text)
        text = re.sub(r"[\.,!\?;:]", "", text)
        text = re.sub(r"[，。！？；：、]", "", text)
        text = re.sub(r"[「」『』【】〔〕［］｛｝（）()〈〉《》]", "", text)
        text = re.sub(r"[・…·•．]", "", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    # 判断答案
    async def judge(self) -> JudgeResult:
        """Judge user answer against the correct answer using lenient string comparison.
        答案(こたえ)を緩(ゆる)く比較(ひかく)します。
        """
        if not self.answer:
            return JudgeResult(
                correct=False,
                error_reason=await self.generate_error_reason(self.answer)
            )

        is_correct = self._normalize_tokens(self.answer) == self._normalize_tokens(self.correct_answer)

        if not is_correct:
            return JudgeResult(
                correct=False,
                error_reason=await self.generate_error_reason(self.answer)
            )

        return JudgeResult(
            correct=True,
            question=self.prompt(),
            answer=f"{self.answer}",
            correct_answer=f"{self.correct_answer}",
            error_reason=None
        )

    # 生成错误原因
    async def generate_error_reason(self) -> str:
        """调用 LLM 生成错误原因。"""
        uow = uow_ctx.get()
        response = await chat_completion(
            input=[
                    SystemMessage(content=f"""
You are the best language learning platform's intelligent judge AI,
you need to generate the user's error reason in a very short way,
use the question's language({uow.target_language}) to generate the error reason.
"""),
                    HumanMessage(content=self.prompt() + f"""
The user's answer is: {self.answer}
                    """)
                ],
            model_type=LLMModel.STANDARD.value["name"]
        )
        return response.content
    
    