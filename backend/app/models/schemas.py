"""
Pydantic模型定义 - 用于API请求和响应的数据验证
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# ==================== 对话相关模型 ====================

class MessageBase_lyl(BaseModel):
    """消息基础模型_lyl"""
    role: str = Field(..., description="消息角色: user 或 assistant")
    content: str = Field(..., description="消息内容")


class MessageCreate_lyl(MessageBase_lyl):
    """创建消息请求模型_lyl"""
    pass


class Message_lyl(MessageBase_lyl):
    """消息响应模型_lyl"""
    id: int
    conversation_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ConversationBase_lyl(BaseModel):
    """对话基础模型_lyl"""
    title: Optional[str] = Field(default="新对话", description="对话标题")


class ConversationCreate_lyl(ConversationBase_lyl):
    """创建对话请求模型_lyl"""
    pass


class Conversation_lyl(ConversationBase_lyl):
    """对话响应模型_lyl"""
    id: int
    created_at: datetime
    updated_at: datetime
    messages: List[Message_lyl] = []
    
    class Config:
        from_attributes = True


class ChatRequest_lyl(BaseModel):
    """聊天请求模型_lyl"""
    message: str = Field(..., description="用户消息")
    conversation_id: Optional[int] = Field(default=None, description="对话ID，为空则创建新对话")
    use_knowledge_base: bool = Field(default=True, description="是否使用知识库")


class ChatResponse_lyl(BaseModel):
    """聊天响应模型_lyl"""
    conversation_id: int
    message: str
    sources: Optional[List[str]] = Field(default=None, description="引用的知识来源")


# ==================== 知识库相关模型 ====================

class DocumentBase_lyl(BaseModel):
    """文档基础模型_lyl"""
    filename: str = Field(..., description="文件名")
    file_type: str = Field(..., description="文件类型")


class DocumentCreate_lyl(DocumentBase_lyl):
    """创建文档请求模型_lyl"""
    content: Optional[str] = Field(default=None, description="文档内容")


class Document_lyl(DocumentBase_lyl):
    """文档响应模型_lyl"""
    id: int
    file_path: str
    file_size: int
    chunk_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class DocumentList_lyl(BaseModel):
    """文档列表响应模型_lyl"""
    total: int
    documents: List[Document_lyl]


# ==================== 通用响应模型 ====================

class SuccessResponse_lyl(BaseModel):
    """成功响应模型_lyl"""
    success: bool = True
    message: str = "操作成功"


class ErrorResponse_lyl(BaseModel):
    """错误响应模型_lyl"""
    success: bool = False
    error: str
    detail: Optional[str] = None

