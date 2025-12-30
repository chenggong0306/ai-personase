"""
Embedding服务模块 - 使用SiliconFlow API进行文本向量化
"""
from typing import List
from langchain_openai import OpenAIEmbeddings

from backend.app.core.config import settings


def create_embeddings_lyl() -> OpenAIEmbeddings:
    """创建Embedding实例_lyl"""
    embeddings = OpenAIEmbeddings(
        model=settings.EMBEDDING_MODEL,
        openai_api_key=settings.EMBEDDING_MODEL_API_KEY,
        openai_api_base=settings.EMBEDDING_MODEL_BASE_URL,
    )
    return embeddings


class EmbeddingService_lyl:
    """Embedding服务类_lyl"""
    
    def __init__(self):
        """初始化Embedding服务_lyl"""
        self._embeddings = None
    
    @property
    def embeddings(self) -> OpenAIEmbeddings:
        """获取Embedding实例_lyl"""
        if self._embeddings is None:
            self._embeddings = create_embeddings_lyl()
        return self._embeddings
    
    async def embed_text_lyl(self, text: str) -> List[float]:
        """向量化单个文本_lyl"""
        return await self.embeddings.aembed_query(text)
    
    async def embed_texts_lyl(self, texts: List[str]) -> List[List[float]]:
        """向量化多个文本_lyl"""
        return await self.embeddings.aembed_documents(texts)


# 全局实例
embedding_service = EmbeddingService_lyl()

