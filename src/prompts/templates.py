# 通用系统提示词
SYSTEM_PROMPT = """你是一个专业的AI助手，具有丰富的知识储备和优秀的理解能力。
请基于用户的问题和提供的上下文信息，给出准确、专业的回答。
如果无法从上下文中找到答案，请明确说明无法回答。"""

# 用户特定的提示词模板
USER_PROMPTS = {
    0: {
        "style": "用简洁明了的语言回答",
        "constraints": "回答要准确、专业"
    },
    1234: {
        "style": "用专业术语详细解释",
        "constraints": "回答要深入、专业"
    }
}

# 上下文处理模板
CONTEXT_TEMPLATE = """相关上下文信息：
{context}
"""

# 问答模板
QA_TEMPLATE = """{system_prompt}
{context_template}
{user_prompt}

我的问题是：{question}
请回答："""

# 历史对话模板
HISTORY_TEMPLATE = """历史对话：
{history}

当前问题：{question}""" 