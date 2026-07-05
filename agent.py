"""ReAct Agent 主循环：思考 -> 工具调用 -> 结果回填 -> 直至输出最终答案。"""
import json

from openai import OpenAI

import config
from tools import TOOLS_SCHEMA, execute_tool

client = OpenAI(api_key=config.API_KEY, base_url=config.BASE_URL)

SYSTEM_PROMPT = """你是一名专业的银行金融顾问助手。
规则：
1. 涉及金融专业知识时，必须先调用 search_knowledge_base 检索，依据资料回答并注明来源；
2. 涉及数值计算时，必须调用 calculator；
3. 知识库中没有相关信息时如实告知，不要编造；
4. 回答使用简洁清晰的中文。"""


def run_agent(user_query: str, history: list | None = None) -> tuple[str, list]:
    """执行一次 Agent 推理，返回 (最终答案, 更新后的对话历史)。"""
    messages = history or [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.append({"role": "user", "content": user_query})

    for step in range(config.MAX_STEPS):
        response = client.chat.completions.create(
            model=config.CHAT_MODEL,
            messages=messages,
            tools=TOOLS_SCHEMA,
        )
        msg = response.choices[0].message

        if msg.tool_calls:
            messages.append(msg.model_dump())
            for tc in msg.tool_calls:
                args = json.loads(tc.function.arguments)
                print(f"  [step {step + 1}] {tc.function.name}({args})")
                result = execute_tool(tc.function.name, args)
                messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})
            continue

        messages.append({"role": "assistant", "content": msg.content})
        return msg.content, messages

    return "抱歉，该问题已超出最大推理轮数。", messages
