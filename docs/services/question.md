# Question

ここは「問題そのもの」を表す層です。  
私は **抽象のベース（QuestionSpec）** を1つだけ決めて、各形式（Choice / Match / Assembly …）を **登録制** で増やす形にしました。  
UoW（`uow_ctx`）とつながっているので、判定や Mistake 生成時に **現在のユーザー・言語** を意識せず使えます。

---

## 目的（ざっくり）

- 形式が違っても **同じ流れ**で扱える（`prompt()` → `judge()` → `Mistake`）
- 追加しやすい（新しい Question を1クラス書いて、`@register_question_type` で登録するだけ）
- LLM を使う部分（エラー理由の生成など）は **必要な時だけ** 呼ぶ

---

## ベース設計：`QuestionSpec`

```python
class QuestionSpec(BaseModel, ABC):
    question_type: QuestionType

    @abstractmethod
    def prompt(self) -> str: ...
    @abstractmethod
    async def judge(self) -> JudgeResult: ...
    @abstractmethod
    async def generate_error_reason(self) -> str: ...

    def to_mistake(self, judge_result: JudgeResult) -> Mistake: ...
    @classmethod
    def from_mistake(cls, mistake: Mistake) -> "QuestionSpec": ...
```

---

## 例：Choic

Swift の **protocol 指向** に近い考え方で、  
**`prompt()` / `judge()` / `generate_error_reason()` を実装して Pydantic に乗れば、それはもう Question** です。  
ここでは一番簡単な Choice を例にします。

```python
from typing import List, Optional, Literal
from pydantic import Field
from app.infra.context import uow_ctx
from app.services.question.base.registry import register_question_type
from app.services.question.base.types import QuestionType

@register_question_type(QuestionType.CHOICE)
class ChoiceQuestion(QuestionSpec):
    """Multiple-choice question (single correct answer)."""

    # 本体（Pydantic フィールド）
    stem: str
    options: List[str]
    correct_answer: str
    # ユーザー回答（未回答のときは None）
    answer: Optional[str] = None

    # 判別子（discriminator）。復元やレジストリ解決に使う
    question_type: Literal[QuestionType.CHOICE] = Field(
        default=QuestionType.CHOICE, description="discriminator"
    )

    def prompt(self) -> str:
        """AI が読むための設問テキスト。"""
        lines = [
            "Choice Question:",
            self.stem,
            "Options:",
            "\n".join(f"- {opt}" for opt in self.options),
        ]
        return "\n".join(lines)

    async def judge(self) -> JudgeResult:
        """回答を判定。間違いのときだけ、短い理由を LLM で作る。"""
        is_correct = (self.answer or "").strip() == self.correct_answer.strip()
        reason: Optional[str] = None
        if not is_correct:
            reason = await self.generate_error_reason()
        return JudgeResult(
            correct=is_correct,
            question=f"{self.stem} Options -> {self.options}",
            answer=self.answer or "",
            correct_answer=self.correct_answer,
            error_reason=reason,
        )

    async def generate_error_reason(self) -> str:
        """LLM に短い誤答理由を作ってもらう（言語は target_language）。"""
        uow = uow_ctx.get()
        # ここでは擬似コード: 実際は chat_completion(...) 等を呼ぶ
        # return await call_llm(system=..., user=..., language=uow.target_language)
        return f"{uow.target_language}: 回答の根拠が選択肢と一致していません。"
```

> ポイント：この最小実装だけで、`QuestionSpec` を満たし、  
> `@register_question_type` でレジストリにも登録されます。  
> あとは Agent / Stack 側で `prompt()` を渡して、`judge()` の `JudgeResult` を受け取るだけです。
