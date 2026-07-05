"""RAG 检索模块：文档切块 -> embedding 向量化 -> 余弦相似度检索。"""
import os

import numpy as np
from openai import OpenAI

import config

client = OpenAI(api_key=config.API_KEY, base_url=config.BASE_URL)

_chunks: list[str] = []
_vectors: np.ndarray | None = None


def _split_into_chunks(text: str) -> list[str]:
    """按段落切块，超长段落按 CHUNK_SIZE 硬切。"""
    chunks = []
    for para in text.split("\n\n"):
        para = para.strip()
        if not para:
            continue
        while len(para) > config.CHUNK_SIZE:
            chunks.append(para[: config.CHUNK_SIZE])
            para = para[config.CHUNK_SIZE :]
        if para:
            chunks.append(para)
    return chunks


def _embed(texts: list[str]) -> np.ndarray:
    resp = client.embeddings.create(model=config.EMBEDDING_MODEL, input=texts)
    return np.array([item.embedding for item in resp.data])


def build_index():
    """读取知识库目录下所有 .md/.txt，构建内存向量索引。"""
    global _chunks, _vectors
    _chunks = []
    for fname in sorted(os.listdir(config.KNOWLEDGE_DIR)):
        if not fname.endswith((".md", ".txt")):
            continue
        with open(os.path.join(config.KNOWLEDGE_DIR, fname), encoding="utf-8") as f:
            _chunks += [f"[来源:{fname}] {c}" for c in _split_into_chunks(f.read())]

    if not _chunks:
        raise RuntimeError(f"知识库目录 {config.KNOWLEDGE_DIR}/ 为空")

    _vectors = _embed(_chunks)
    print(f"[RAG] 索引构建完成：{len(_chunks)} 个文本块")


def search(query: str) -> str:
    """返回与 query 余弦相似度最高的 TOP_K 个文本块。"""
    q_vec = _embed([query])[0]
    sims = _vectors @ q_vec / (np.linalg.norm(_vectors, axis=1) * np.linalg.norm(q_vec))
    top_idx = np.argsort(sims)[::-1][: config.TOP_K]
    return "\n---\n".join(f"(相关度 {sims[i]:.2f}) {_chunks[i]}" for i in top_idx)
