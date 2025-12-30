"""
文档处理服务模块 - 处理文档的加载、分割和存储
"""
import os
import shutil
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
    Docx2txtLoader,
    UnstructuredMarkdownLoader,
)
from langchain_core.documents import Document

from backend.app.core.config import settings
from backend.app.database.database import db_manager


class DocumentService_lyl:
    """文档服务类_lyl"""
    
    def __init__(self):
        """初始化文档服务_lyl"""
        self.documents_path = Path(settings.DOCUMENTS_PATH)
        self.documents_path.mkdir(parents=True, exist_ok=True)
        
        # 文本分割器配置
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            length_function=len,
            separators=["\n\n", "\n", "。", "！", "？", ".", "!", "?", " ", ""]
        )
    
    def get_loader_lyl(self, file_path: str) -> Optional[Any]:
        """根据文件类型获取对应的加载器_lyl"""
        file_ext = Path(file_path).suffix.lower()
        
        loaders = {
            ".txt": TextLoader,
            ".pdf": PyPDFLoader,
            ".docx": Docx2txtLoader,
            ".doc": Docx2txtLoader,
            ".md": UnstructuredMarkdownLoader,
        }
        
        loader_class = loaders.get(file_ext)
        if loader_class:
            try:
                return loader_class(file_path, encoding="utf-8") if file_ext == ".txt" else loader_class(file_path)
            except Exception:
                return loader_class(file_path)
        return None
    
    async def load_and_split_document_lyl(self, file_path: str) -> List[Document]:
        """加载并分割文档_lyl"""
        loader = self.get_loader_lyl(file_path)
        if not loader:
            raise ValueError(f"不支持的文件类型: {Path(file_path).suffix}")
        
        documents = loader.load()
        chunks = self.text_splitter.split_documents(documents)
        
        # 为每个chunk添加元数据
        for i, chunk in enumerate(chunks):
            chunk.metadata["chunk_index"] = i
            chunk.metadata["source_file"] = Path(file_path).name
        
        return chunks
    
    async def save_uploaded_file_lyl(self, filename: str, content: bytes) -> str:
        """保存上传的文件_lyl"""
        # 生成唯一文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{filename}"
        file_path = self.documents_path / safe_filename
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        return str(file_path)
    
    async def delete_file_lyl(self, file_path: str) -> bool:
        """删除文件_lyl"""
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
            return True
        except Exception:
            return False
    
    async def get_all_documents_lyl(self) -> List[Dict[str, Any]]:
        """获取所有文档记录_lyl"""
        return await db_manager.fetch_all_lyl(
            "SELECT * FROM documents ORDER BY created_at DESC"
        )
    
    async def get_document_by_id_lyl(self, doc_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取文档_lyl"""
        return await db_manager.fetch_one_lyl(
            "SELECT * FROM documents WHERE id = ?", (doc_id,)
        )
    
    async def add_document_record_lyl(
        self, filename: str, file_type: str, file_path: str, 
        file_size: int, chunk_count: int
    ) -> int:
        """添加文档记录_lyl"""
        cursor = await db_manager.execute_lyl(
            """INSERT INTO documents (filename, file_type, file_path, file_size, chunk_count)
               VALUES (?, ?, ?, ?, ?)""",
            (filename, file_type, file_path, file_size, chunk_count)
        )
        return cursor.lastrowid
    
    async def delete_document_record_lyl(self, doc_id: int) -> bool:
        """删除文档记录_lyl"""
        await db_manager.execute_lyl("DELETE FROM documents WHERE id = ?", (doc_id,))
        return True


# 全局实例
document_service = DocumentService_lyl()

