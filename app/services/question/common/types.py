from enum import Enum


class QuestionType(str, Enum):
    """Simplified identifiers for each question kind."""

    CHOICE = "choice"             # 选择题
    MATCH_AUDIO = "match_audio"    # 音频 ↔︎ 文本连连看
    MATCH_NATIVE = "match_native"  # 母语 ↔︎ 目标语连连看
    CLOZE = "cloze"               # 选词填空 / 词块拼接
    ORDER = "order"               # 句子/片段排序
    FREE = "free"                 # 自由回答
    FREE_LIMIT = "free_limit"     # 含指定语法/单词的自由回答
    ROLEPLAY = "roleplay"         # 角色扮演达成意图

