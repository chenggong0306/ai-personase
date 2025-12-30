"""
对话服务模块 - 管理对话和消息的增删改查
"""
from typing import List, Dict, Any, Optional
from datetime import datetime

from backend.app.database.database import db_manager


class ConversationService_lyl:
    """对话服务类_lyl"""
    
    async def create_conversation_lyl(self, title: str = "新对话") -> Dict[str, Any]:
        """创建新对话_lyl"""
        cursor = await db_manager.execute_lyl(
            "INSERT INTO conversations (title) VALUES (?)",
            (title,)
        )
        conversation_id = cursor.lastrowid
        
        return await self.get_conversation_by_id_lyl(conversation_id)
    
    async def get_conversation_by_id_lyl(self, conversation_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取对话_lyl"""
        conversation = await db_manager.fetch_one_lyl(
            "SELECT * FROM conversations WHERE id = ?",
            (conversation_id,)
        )
        
        if conversation:
            # 获取对话的消息
            messages = await self.get_messages_by_conversation_id_lyl(conversation_id)
            conversation["messages"] = messages
        
        return conversation
    
    async def get_all_conversations_lyl(self) -> List[Dict[str, Any]]:
        """获取所有对话_lyl"""
        conversations = await db_manager.fetch_all_lyl(
            "SELECT * FROM conversations ORDER BY updated_at DESC"
        )
        
        # 为每个对话获取消息数量
        for conv in conversations:
            count = await db_manager.fetch_one_lyl(
                "SELECT COUNT(*) as count FROM messages WHERE conversation_id = ?",
                (conv["id"],)
            )
            conv["message_count"] = count["count"] if count else 0
        
        return conversations
    
    async def update_conversation_title_lyl(
        self, 
        conversation_id: int, 
        title: str
    ) -> bool:
        """更新对话标题_lyl"""
        await db_manager.execute_lyl(
            "UPDATE conversations SET title = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (title, conversation_id)
        )
        return True
    
    async def delete_conversation_lyl(self, conversation_id: int) -> bool:
        """删除对话_lyl"""
        # 先删除消息
        await db_manager.execute_lyl(
            "DELETE FROM messages WHERE conversation_id = ?",
            (conversation_id,)
        )
        # 再删除对话
        await db_manager.execute_lyl(
            "DELETE FROM conversations WHERE id = ?",
            (conversation_id,)
        )
        return True
    
    async def add_message_lyl(
        self, 
        conversation_id: int, 
        role: str, 
        content: str
    ) -> Dict[str, Any]:
        """添加消息_lyl"""
        cursor = await db_manager.execute_lyl(
            "INSERT INTO messages (conversation_id, role, content) VALUES (?, ?, ?)",
            (conversation_id, role, content)
        )
        
        # 更新对话的更新时间
        await db_manager.execute_lyl(
            "UPDATE conversations SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (conversation_id,)
        )
        
        return await db_manager.fetch_one_lyl(
            "SELECT * FROM messages WHERE id = ?",
            (cursor.lastrowid,)
        )
    
    async def get_messages_by_conversation_id_lyl(
        self, 
        conversation_id: int
    ) -> List[Dict[str, Any]]:
        """获取对话的所有消息_lyl"""
        return await db_manager.fetch_all_lyl(
            "SELECT * FROM messages WHERE conversation_id = ? ORDER BY created_at ASC",
            (conversation_id,)
        )
    
    async def get_recent_messages_lyl(
        self, 
        conversation_id: int, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """获取最近的消息用于上下文_lyl"""
        messages = await db_manager.fetch_all_lyl(
            """SELECT * FROM messages 
               WHERE conversation_id = ? 
               ORDER BY created_at DESC 
               LIMIT ?""",
            (conversation_id, limit)
        )
        # 反转顺序，使最早的消息在前
        return list(reversed(messages))
    
    async def auto_generate_title_lyl(
        self, 
        conversation_id: int, 
        first_message: str
    ) -> str:
        """根据第一条消息自动生成标题_lyl"""
        # 截取前30个字符作为标题
        title = first_message[:30]
        if len(first_message) > 30:
            title += "..."
        
        await self.update_conversation_title_lyl(conversation_id, title)
        return title


# 全局实例
conversation_service = ConversationService_lyl()

