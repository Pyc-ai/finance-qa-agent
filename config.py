"""全局配置。API Key 通过环境变量注入，不要写入代码。"""
import os

API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"

CHAT_MODEL = "qwen-plus"
EMBEDDING_MODEL = "text-embedding-v3"

KNOWLEDGE_DIR = "knowledge_base"
CHUNK_SIZE = 300   # 文本块最大字数
TOP_K = 3          # 检索返回的文本块数量

MAX_STEPS = 6      # Agent 最大推理轮数
