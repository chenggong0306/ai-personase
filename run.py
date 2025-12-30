"""
启动脚本 - 个性化知识问答系统后端启动入口
使用方式: uv run run.py
"""
import uvicorn


def main_lyl():
    """启动FastAPI应用_lyl"""
    uvicorn.run(
        "backend.app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )


if __name__ == "__main__":
    main_lyl()

