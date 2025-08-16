from app.infra.models.grammar import Grammar
from app.services.common.grammar import GrammarService
from app.infra.context import uow_ctx

async def add_grammar(
    name: str,
    usage: str,
) -> str:
    grammar: Grammar = await GrammarService().create({"name": name, "usage": usage, "language": uow_ctx.get().target_language})
    return f"""
grammar added:
id: {grammar.id}
name: {name}
usage: {usage}
language: {uow_ctx.get().target_language}
updated_at: {grammar.updated_at.isoformat()}
"""

# 给Grammar记录一次correct/incorrect
async def record_grammar(grammar_id: int,correct: bool) -> str:
    grammar: Grammar = await GrammarService().record_grammar(grammar_id, correct)
    return f"""
grammar recorded:
id: {grammar.id}
correct: {correct}
updated_at: {grammar.updated_at.isoformat()}
"""

async def add_and_record_grammar(name: str, usage: str, correct: bool) -> Grammar:
    return await GrammarService().add_and_record_grammar(name, usage, correct)