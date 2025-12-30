"""
配置模块 - 加载环境变量和应用配置
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings


def load_env_lyl() -> None:
    """加载环境变量_lyl"""
    # 从项目根目录加载.env文件
    root_dir = Path(__file__).parent.parent.parent.parent
    env_path = root_dir / ".env"
    load_dotenv(env_path)


# 加载环境变量
load_env_lyl()


class Settings_lyl(BaseSettings):
    """应用配置类_lyl"""
    
    # 项目信息
    PROJECT_NAME: str = "个性化知识问答系统"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"
    
    # DeepSeek LLM 配置
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
    
    # Embedding 模型配置
    EMBEDDING_MODEL_API_KEY: str = os.getenv("EMBEDDING_MODEL_API_KEY", "")
    EMBEDDING_MODEL_BASE_URL: str = os.getenv("EMBEDDING_MODEL_BASE_URL", "https://api.siliconflow.cn/v1")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3")
    
    # 数据库配置
    DATABASE_URL: str = "data/knowledge_qa.db"
    
    # 向量存储配置
    VECTOR_STORE_PATH: str = "data/vector_store"
    
    # 文档存储配置
    DOCUMENTS_PATH: str = "data/documents"
    
    # CORS配置
    CORS_ORIGINS: list = ["*"]  # 允许所有来源
    
    class Config:
        env_file = ".env"
        extra = "allow"


def get_settings_lyl() -> Settings_lyl:
    """获取配置实例_lyl"""
    return Settings_lyl()


settings = get_settings_lyl()

