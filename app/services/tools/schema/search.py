{
    "type": "function",
    "function": {
    "name": "search_resource",
    "description": """ 
    检索用户在Vounica中记录的资源
    如果你使用regex查询, regex应该是一个正则表达式, 用于匹配资源的内容
    如果你使用vector查询, vector应该是一个字符串, 用于语意匹配资源, 注意vector时多语言的
    
    Vocab
    可以检索name和usage两个字段, 其中usage通过LLM生成, 表示了这个usage的使用场景
    return: 
    {
        "name": "单词",
        "usage": "单词的使用场景",
        "status": "单词的习得状态, 这是最近N次练习中, 单词被正确使用的概率, 从0-1"
    }
    
    
    Grammar
    可以检索name和usage两个字段, 其中usage通过LLM生成, 表示了这个usage的使用场景
    return: 
    {
        "name": "语法",
        "usage": "语法的使用场景",
        "status": "语法被正确使用的概率, 从0-1“
    }
    
    Memory
    Content: 记忆内容, 记忆内容需要可以被string化, 只能由LLM主动生成添加, 这里代表了你自己对这个用户的记忆
    return: 
    {
        "content": "记忆内容",
        "status": "记忆被正确使用的概率, 从0-1"
    }
    
    
    Story
    Content: 故事内容, 这里代表了用户自己记录的故事
    Summary: 故事概要, 这里代表了你阅读这个故事后对故事的总结, 只能由LLM主动生成添加
    return: 
    {
        "content": "故事内容",
        "summary": "故事概要",
        "category": "故事分类"
    }
    
    
    Mistake
    Question: 错误题目的内容
    Answer: 错题答案
    Correct_Answer: 正确答案
    Error_Reason: 错误原因, 只能由LLM根据回答主动生成添加
    return: 
    {
        "question": "错题题目",
        "question_type": "错题题目类型",
        "answer": "错题答案",
        "correct_answer": "正确答案",
        "error_reason": "错误原因"
    }
    
    支持的资源
    vocab.name 
    vocab.usage
    grammar.name
    grammar.usage
    memory.content
    story.content
    story.summary
    story.category
    mistake.question
    mistake.answer
    mistake.correct_answer
    mistake.error_reason
    
    
    """,
    "parameters": {
        "type": "object",
        "properties": {
            "resource": {
                "type": "string",
                "enum": ["vocab", "grammar", "mistake", "story", "memory"],
            },
            "field": {"type": "string"},
            "method": {"type": "string", "enum": ["regex", "vector"], "default": "regex"},
            "query": {"type": "string"},
            "limit": {"type": "integer", "default": 20},
        },
        "required": ["resource", "field", "query"],
        },
    },
}
