#question_stack 
from app.services.tools.langchain.question.choice import ChoiceQuestion
from app.services.agent.question.agent import QuestionAgentResult




# 制作几个question
choice_question = ChoiceQuestion(
    stem="What is the capital of France?",
    options=["Paris", "London", "Berlin", "Madrid"],
    correct_answer="Paris",
    language="en"
)

questions = []
for i in range(10):
    questions.append(choice_question)

print(questions)
Result = QuestionAgentResult(data=questions)


print(Result.model_dump_json())
