# 后端 Dockerfile - Python + FastAPI + uv
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 换成清华镜像源
RUN sed -i 's/deb.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list.d/debian.sources

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 配置 pip 清华镜像源并安装 uv
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip install uv

# 复制依赖文件（从项目根目录）
COPY pyproject.toml uv.lock ./

# 安装 Python 依赖
RUN uv sync

# 复制后端应用代码
COPY backend/ ./backend/

# 设置 tiktoken 缓存目录（避免运行时下载）
ENV TIKTOKEN_CACHE_DIR=/app/backend/tiktoken_cache

# 创建数据目录
RUN mkdir -p /app/data/documents /app/data/vector_store

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uv", "run", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]

