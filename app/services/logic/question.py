from app.services.question.types import QuestionUnion
from app.services.question.base.spec import QuestionSpec, JudgeResult
from app.services.common.mistake import MistakeService
from app.infra.context import uow_ctx
from typing import List
import asyncio

class QuestionHandler:
    def __init__(self):
        self._uow = uow_ctx.get()
        
    
    # 处理题目, 判断错误, 并且存入mistake表
    async def judge(self, question: QuestionUnion, answer: str) -> JudgeResult:
        # 判断错误
        judge_result: JudgeResult = await question.judge(answer)
        return judge_result
    
    # 记录用户的回答（同时并发执行 judge，不做限流与去重）
    async def record(self, questions: List[QuestionSpec], answer: str) -> List[JudgeResult]:
        # 这里的questions应该是前端传回来的log列表, 可能会有重复的题目, 但是重复代表用户错误了多次, 应该记录多次错题集
        results: List[JudgeResult] = await asyncio.gather(
            *(self.judge(q, answer) for q in questions),
            return_exceptions=False,
        )

        # 按原始顺序逐条记录错误（即使是重复题，也按出现次数记录）
        for question, judge_result in zip(questions, results):
            if not judge_result.correct:
                # 存入mistake表
                self._uow.db.add(question.to_mistake(judge_result))
        return results
    