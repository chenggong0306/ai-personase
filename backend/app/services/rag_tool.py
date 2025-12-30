"""
RAG工具模块 - 将RAG封装为LangChain工具供Agent使用
使用LangChain v1.0的@tool装饰器方式
"""
import asyncio
import json
from langchain.tools import tool

from backend.app.core.logger import log_lyl
from backend.app.services.vector_store_service import vector_store_service

# 全局变量存储最近的检索结果，供前端溯源使用
_last_search_sources_lyl: list = []


def get_last_sources_lyl() -> list:
    """获取最近一次检索的来源列表_lyl"""
    global _last_search_sources_lyl
    return _last_search_sources_lyl


def clear_sources_lyl():
    """清空来源列表_lyl"""
    global _last_search_sources_lyl
    _last_search_sources_lyl = []


async def search_knowledge_base_async_lyl(query: str) -> str:
    """异步搜索知识库_lyl"""
    global _last_search_sources_lyl
    log_lyl.info(f"RAG工具: 开始搜索知识库，query: {query[:50]}...")
    try:
        # 搜索相关文档
        results = await vector_store_service.search_lyl(query, k=3)

        if not results:
            log_lyl.info("RAG工具: 未找到相关信息")
            return "未在知识库中找到相关信息。"

        log_lyl.info(f"RAG工具: 找到 {len(results)} 个相关文档")

        # 存储结构化来源信息供前端使用
        _last_search_sources_lyl = []
        formatted_results = []

        for i, result in enumerate(results, 1):
            source_file = result["metadata"].get("source_file", "未知来源")
            content = result["content"]

            # 保存结构化信息
            _last_search_sources_lyl.append({
                "id": i,
                "source": source_file,
                "content": content[:500] + "..." if len(content) > 500 else content
            })

            # 返回给LLM的格式，提示使用[1][2]标记
            formatted_results.append(
                f"[{i}] 来源文件: {source_file}\n内容: {content}"
            )

        return "\n\n---\n\n".join(formatted_results)

    except Exception as e:
        log_lyl.error(f"RAG工具: 检索失败 - {str(e)}")
        return f"检索知识库时发生错误: {str(e)}"


@tool
def knowledge_base_search_lyl(query: str) -> str:
    """从个人知识库中检索相关信息的工具。
    当用户询问的问题可能与知识库中的文档相关时，使用此工具搜索相关内容。
    输入应该是用户问题的关键部分或完整问题。
    返回知识库中与问题最相关的文档片段。

    Args:
        query: 用户的问题或查询内容

    Returns:
        知识库中与问题最相关的文档片段
    """
    # 在同步上下文中运行异步函数
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # 如果事件循环正在运行，创建新任务
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    asyncio.run,
                    search_knowledge_base_async_lyl(query)
                )
                return future.result()
        else:
            return loop.run_until_complete(search_knowledge_base_async_lyl(query))
    except RuntimeError:
        # 没有事件循环，创建新的
        return asyncio.run(search_knowledge_base_async_lyl(query))


def get_rag_tools_lyl() -> list:
    """获取RAG工具列表_lyl"""
    return [knowledge_base_search_lyl]

