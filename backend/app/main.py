"""
FastAPI应用主入口 - 个性化知识问答系统后端
"""
import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.app.core.config import settings
from backend.app.core.logger import log_lyl
from backend.app.database.database import db_manager
from backend.app.services.vector_store_service import vector_store_service
from backend.app.api import chat, knowledge


def get_static_path_lyl():
    """获取静态文件路径_lyl"""
    if getattr(sys, 'frozen', False):
        # PyInstaller 打包后的路径
        base_path = sys._MEIPASS
    else:
        # 开发环境路径
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    static_path = os.path.join(base_path, 'backend', 'static')
    return static_path if os.path.exists(static_path) else None


@asynccontextmanager
async def lifespan_lyl(app: FastAPI):
    """应用生命周期管理_lyl"""
    # 启动时执行
    log_lyl.info("🚀 正在启动个性化知识问答系统...")

    # 初始化数据库
    await db_manager.init_tables_lyl()
    log_lyl.success("✅ 数据库初始化完成")

    # 初始化向量存储
    await vector_store_service.initialize_lyl()
    log_lyl.success("✅ 向量存储初始化完成")

    log_lyl.info(f"🌟 {settings.PROJECT_NAME} v{settings.VERSION} 启动成功!")
    log_lyl.info(f"📖 API文档: http://localhost:8000/docs")

    yield

    # 关闭时执行
    log_lyl.info("👋 正在关闭系统...")
    await db_manager.disconnect_lyl()
    log_lyl.success("✅ 系统已安全关闭")


def create_app_lyl() -> FastAPI:
    """创建FastAPI应用实例_lyl"""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="""
        个性化知识问答系统 API
        
        ## 功能特性
        
        * 🤖 **智能对话** - 基于DeepSeek大模型的智能问答
        * 📚 **知识库管理** - 上传、管理个人知识文档
        * 🔍 **RAG检索** - 从知识库中检索相关信息辅助回答
        * 💬 **对话历史** - 保存和管理历史对话记录
        
        ## 技术栈
        
        * FastAPI + LangChain + DeepSeek
        * FAISS向量数据库 + BGE-M3嵌入模型
        * aiosqlite异步数据库
        """,
        lifespan=lifespan_lyl,
    )
    
    # 配置CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 注册路由
    app.include_router(chat.router, prefix=settings.API_PREFIX)
    app.include_router(knowledge.router, prefix=settings.API_PREFIX)

    # 挂载静态文件（用于exe打包后serve前端）
    static_path = get_static_path_lyl()
    if static_path:
        app.mount("/assets", StaticFiles(directory=os.path.join(static_path, "assets")), name="assets")

    return app


# 创建应用实例
app = create_app_lyl()


@app.get("/")
async def root_lyl():
    """根路径_lyl - 返回前端页面或API信息"""
    static_path = get_static_path_lyl()
    if static_path:
        index_path = os.path.join(static_path, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check_lyl():
    """健康检查_lyl"""
    return {"status": "healthy"}


@app.get("/{path:path}")
async def serve_spa_lyl(path: str):
    """SPA路由支持_lyl - 所有前端路由返回index.html"""
    static_path = get_static_path_lyl()
    if static_path:
        # 先尝试返回静态文件
        file_path = os.path.join(static_path, path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        # 否则返回 index.html（SPA路由）
        index_path = os.path.join(static_path, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
    return {"error": "Not found"}

