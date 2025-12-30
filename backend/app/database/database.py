"""
数据库管理模块 - 使用aiosqlite实现异步SQLite操作
"""
import aiosqlite
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

from backend.app.core.config import settings


class DatabaseManager_lyl:
    """数据库管理类_lyl"""
    
    def __init__(self):
        """初始化数据库管理器_lyl"""
        self.db_path = Path(settings.DATABASE_URL)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._connection: Optional[aiosqlite.Connection] = None
    
    async def connect_lyl(self) -> aiosqlite.Connection:
        """连接数据库_lyl"""
        if self._connection is None:
            self._connection = await aiosqlite.connect(str(self.db_path))
            self._connection.row_factory = aiosqlite.Row
        return self._connection
    
    async def disconnect_lyl(self) -> None:
        """断开数据库连接_lyl"""
        if self._connection:
            await self._connection.close()
            self._connection = None
    
    async def init_tables_lyl(self) -> None:
        """初始化数据库表_lyl"""
        conn = await self.connect_lyl()
        
        # 创建对话表
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT DEFAULT '新对话',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 创建消息表
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
            )
        """)
        
        # 创建文档表
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                file_type TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_size INTEGER DEFAULT 0,
                chunk_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        await conn.commit()
    
    async def execute_lyl(self, query: str, params: tuple = ()) -> aiosqlite.Cursor:
        """执行SQL查询_lyl"""
        conn = await self.connect_lyl()
        cursor = await conn.execute(query, params)
        await conn.commit()
        return cursor
    
    async def fetch_one_lyl(self, query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        """查询单条记录_lyl"""
        conn = await self.connect_lyl()
        cursor = await conn.execute(query, params)
        row = await cursor.fetchone()
        if row:
            return dict(row)
        return None
    
    async def fetch_all_lyl(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """查询多条记录_lyl"""
        conn = await self.connect_lyl()
        cursor = await conn.execute(query, params)
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


# 全局数据库实例
db_manager = DatabaseManager_lyl()


async def get_db_lyl() -> DatabaseManager_lyl:
    """获取数据库实例_lyl"""
    return db_manager

