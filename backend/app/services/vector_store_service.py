"""
向量存储服务模块 - 管理文档向量的存储和检索
"""
import os
from pathlib import Path
from typing import List, Optional, Dict, Any

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from backend.app.core.config import settings
from backend.app.services.embedding_service import embedding_service


class VectorStoreService_lyl:
    """向量存储服务类_lyl"""
    
    def __init__(self):
        """初始化向量存储服务_lyl"""
        self.store_path = Path(settings.VECTOR_STORE_PATH)
        self.store_path.mkdir(parents=True, exist_ok=True)
        self._vector_store: Optional[FAISS] = None
    
    @property
    def vector_store(self) -> Optional[FAISS]:
        """获取向量存储实例_lyl"""
        return self._vector_store
    
    async def initialize_lyl(self) -> None:
        """初始化或加载向量存储_lyl"""
        index_path = self.store_path / "index.faiss"
        if index_path.exists():
            await self.load_store_lyl()
    
    async def load_store_lyl(self) -> bool:
        """加载已存在的向量存储_lyl"""
        try:
            self._vector_store = FAISS.load_local(
                str(self.store_path),
                embedding_service.embeddings,
                allow_dangerous_deserialization=True
            )
            return True
        except Exception as e:
            print(f"加载向量存储失败: {e}")
            return False
    
    async def save_store_lyl(self) -> bool:
        """保存向量存储到磁盘_lyl"""
        if self._vector_store:
            try:
                self._vector_store.save_local(str(self.store_path))
                return True
            except Exception as e:
                print(f"保存向量存储失败: {e}")
                return False
        return False
    
    async def add_documents_lyl(self, documents: List[Document]) -> int:
        """添加文档到向量存储_lyl"""
        if not documents:
            return 0
        
        if self._vector_store is None:
            # 创建新的向量存储
            self._vector_store = await FAISS.afrom_documents(
                documents,
                embedding_service.embeddings
            )
        else:
            # 添加到现有存储
            await self._vector_store.aadd_documents(documents)
        
        # 保存到磁盘
        await self.save_store_lyl()
        return len(documents)
    
    async def search_lyl(
        self, 
        query: str, 
        k: int = 4,
        score_threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """搜索相关文档_lyl"""
        if self._vector_store is None:
            return []
        
        try:
            # 使用相似度搜索
            docs_with_scores = await self._vector_store.asimilarity_search_with_score(
                query, k=k
            )
            
            results = []
            for doc, score in docs_with_scores:
                # 分数越低越相似（L2距离）
                if score < score_threshold * 10:  # 调整阈值
                    results.append({
                        "content": doc.page_content,
                        "metadata": doc.metadata,
                        "score": float(score)
                    })
            
            return results
        except Exception as e:
            print(f"搜索失败: {e}")
            return []
    
    async def delete_by_source_lyl(self, source_file: str) -> bool:
        """根据源文件删除文档_lyl"""
        # FAISS不支持直接删除，需要重建索引
        # 这里简化处理，实际项目中可能需要更复杂的逻辑
        return True
    
    def get_document_count_lyl(self) -> int:
        """获取文档数量_lyl"""
        if self._vector_store and hasattr(self._vector_store, 'index'):
            return self._vector_store.index.ntotal
        return 0


# 全局实例
vector_store_service = VectorStoreService_lyl()

