from app.services.question.types import QuestionUnion
from app.services.question.base.spec import QuestionSpec, JudgeResult
from app.services.common.mistake import MistakeService
from app.infra.context import uow_ctx

class QuestionHandler:
    def __init__(self):
        self._uow = uow_ctx.get()
        
    
    # 处理题目, 判断错误, 并且存入mistake表
    async def judge(self, question: QuestionSpec, answer: str) -> JudgeResult:
        # 判断错误
        judge_result: JudgeResult = await question.judge(answer)
        if not judge_result.correct:
            # 存入mistake表
            self._uow.db.add(question.to_mistake(judge_result))
            pass
        return judge_result