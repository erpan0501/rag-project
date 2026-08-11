"""零配置本地演示向量。

它不是生产级语义模型，而是稳定、可重复的字符哈希向量，
用于在没有 Embedding API Key 或模型文件时演示上传和检索链路。
"""
import hashlib
import math
from typing import List

from src.embeddings.base import BaseEmbedding


class DemoEmbedding(BaseEmbedding):
    DIMENSION = 64

    def _embed(self, text: str) -> List[float]:
        vector = [0.0] * self.DIMENSION
        for char in text.strip().lower():
            digest = hashlib.sha1(char.encode('utf-8')).digest()
            index = int.from_bytes(digest[:4], 'big') % self.DIMENSION
            vector[index] += 1.0
        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / norm for value in vector]

    def embed_text(self, text: str) -> List[float]:
        return self._embed(text)

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return [self._embed(text) for text in texts]

    def get_dimension(self) -> int:
        return self.DIMENSION

    def get_model_name(self) -> str:
        return 'local-demo-hash-64'
