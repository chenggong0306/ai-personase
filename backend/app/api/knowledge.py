"""
知识库API路由 - 处理文档上传、管理相关的请求
"""
import os
from typing import List
from fastapi import APIRouter, HTTPException, UploadFile, File

from backend.app.core.logger import log_lyl
from backend.app.models.schemas import (
    Document_lyl,
    DocumentList_lyl,
    SuccessResponse_lyl,
)
from backend.app.services.document_service import document_service
from backend.app.services.vector_store_service import vector_store_service

router = APIRouter(prefix="/knowledge", tags=["知识库"])

# 支持的文件类型
ALLOWED_EXTENSIONS = {".txt", ".pdf", ".docx", ".doc", ".md"}


def validate_file_extension_lyl(filename: str) -> bool:
    """验证文件扩展名_lyl"""
    ext = os.path.splitext(filename)[1].lower()
    return ext in ALLOWED_EXTENSIONS


@router.post("/upload")
async def upload_document_lyl(file: UploadFile = File(...)):
    """
    上传文档到知识库_lyl

    支持的文件类型: txt, pdf, docx, doc, md
    """
    log_lyl.info(f"收到文件上传请求: {file.filename}")
    try:
        # 验证文件类型
        if not validate_file_extension_lyl(file.filename):
            log_lyl.warning(f"不支持的文件类型: {file.filename}")
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件类型。支持的类型: {', '.join(ALLOWED_EXTENSIONS)}"
            )

        # 读取文件内容
        content = await file.read()
        file_size = len(content)
        log_lyl.debug(f"文件大小: {file_size} bytes")

        # 保存文件
        file_path = await document_service.save_uploaded_file_lyl(file.filename, content)
        log_lyl.debug(f"文件已保存: {file_path}")

        # 获取文件类型
        file_ext = os.path.splitext(file.filename)[1].lower()

        # 加载并分割文档
        chunks = await document_service.load_and_split_document_lyl(file_path)
        log_lyl.info(f"文档分割完成，共 {len(chunks)} 个块")

        # 添加到向量存储
        await vector_store_service.add_documents_lyl(chunks)
        log_lyl.info("文档已添加到向量存储")

        # 保存文档记录到数据库
        doc_id = await document_service.add_document_record_lyl(
            filename=file.filename,
            file_type=file_ext,
            file_path=file_path,
            file_size=file_size,
            chunk_count=len(chunks)
        )

        log_lyl.success(f"文档上传成功: {file.filename}, ID: {doc_id}")
        return {
            "success": True,
            "message": "文档上传成功",
            "document_id": doc_id,
            "filename": file.filename,
            "chunk_count": len(chunks)
        }

    except HTTPException:
        raise
    except Exception as e:
        log_lyl.error(f"文档上传失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")


@router.get("/documents")
async def get_documents_lyl():
    """获取所有文档列表_lyl"""
    documents = await document_service.get_all_documents_lyl()
    return DocumentList_lyl(
        total=len(documents),
        documents=documents
    )


@router.get("/documents/{document_id}")
async def get_document_lyl(document_id: int):
    """获取单个文档详情_lyl"""
    document = await document_service.get_document_by_id_lyl(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="文档不存在")
    return document


@router.delete("/documents/{document_id}")
async def delete_document_lyl(document_id: int):
    """删除文档_lyl"""
    try:
        # 获取文档信息
        document = await document_service.get_document_by_id_lyl(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="文档不存在")
        
        # 删除物理文件
        await document_service.delete_file_lyl(document["file_path"])
        
        # 删除数据库记录
        await document_service.delete_document_record_lyl(document_id)
        
        # 注意：FAISS不支持直接删除，如需完全删除需要重建索引
        
        return SuccessResponse_lyl(message="文档删除成功")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")


@router.get("/search")
async def search_knowledge_lyl(query: str, k: int = 5):
    """搜索知识库_lyl"""
    try:
        results = await vector_store_service.search_lyl(query, k=k)
        return {
            "query": query,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


@router.get("/stats")
async def get_knowledge_stats_lyl():
    """获取知识库统计信息_lyl"""
    documents = await document_service.get_all_documents_lyl()
    total_chunks = sum(doc.get("chunk_count", 0) for doc in documents)
    total_size = sum(doc.get("file_size", 0) for doc in documents)

    # 统计文件类型分布
    file_types: dict[str, int] = {}
    for doc in documents:
        ft = doc.get("file_type", "").lstrip(".")
        if ft:
            file_types[ft] = file_types.get(ft, 0) + 1

    return {
        "total_documents": len(documents),
        "total_chunks": total_chunks,
        "total_size_bytes": total_size,
        "vector_count": vector_store_service.get_document_count_lyl(),
        "file_types": file_types
    }

