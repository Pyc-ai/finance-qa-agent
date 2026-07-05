"""工具定义与执行：知识库检索 / 计算器 / 日期。"""
import ast
import operator
from datetime import date

import rag


def search_knowledge_base(query: str) -> str:
    return rag.search(query)


# 计算器：ast 白名单解析，避免 eval() 的注入风险
_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
        ast.Div: operator.truediv, ast.Pow: operator.pow, ast.USub: operator.neg}


def _safe_eval(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_safe_eval(node.operand))
    raise ValueError("仅支持加减乘除和乘方")


def calculator(expression: str) -> str:
    try:
        return str(_safe_eval(ast.parse(expression, mode="eval").body))
    except Exception as e:
        return f"计算出错：{e}"


def get_current_date() -> str:
    return date.today().isoformat()


TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "search_knowledge_base",
            "description": "在金融知识库中检索资料。涉及信用卡、贷款、利率等专业知识时必须先调用，不要凭记忆回答。",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string", "description": "检索关键词，如：房贷提前还款规则"}},
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "计算数学表达式。涉及利息、月供等数值计算时必须使用，禁止心算。",
            "parameters": {
                "type": "object",
                "properties": {"expression": {"type": "string", "description": "如 300000*0.045/12"}},
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_date",
            "description": "获取今天的日期。",
            "parameters": {"type": "object", "properties": {}},
        },
    },
]

TOOL_FUNCTIONS = {
    "search_knowledge_base": search_knowledge_base,
    "calculator": calculator,
    "get_current_date": get_current_date,
}


def execute_tool(name: str, arguments: dict) -> str:
    if name not in TOOL_FUNCTIONS:
        return f"错误：工具 {name} 不存在"
    try:
        return TOOL_FUNCTIONS[name](**arguments)
    except Exception as e:
        return f"工具执行出错：{e}"
