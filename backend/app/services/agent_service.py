"""
Agent服务模块 - 使用LangChain v1.0的create_agent创建智能代理
支持SSE流式输出
"""
from typing import List, Dict, Any, Optional, AsyncGenerator
import json

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

from backend.app.core.config import settings
from backend.app.core.logger import log_lyl
from backend.app.services.rag_tool import get_rag_tools_lyl, get_last_sources_lyl, clear_sources_lyl


# 系统提示词 - 让LLM使用[1][2]等标记引用来源
SYSTEM_PROMPT_LYL = """你是一个智能的个人知识助手，名叫"小知"。你的主要职责是帮助用户回答问题，并在需要时从用户的个人知识库中检索相关信息。

## 你的能力：
1. 回答各类问题，提供有帮助的信息
2. 使用知识库检索工具从用户的文档中查找相关内容
3. 综合知识库信息和自身知识给出全面的回答

## 工作原则：
1. 当用户的问题可能与其知识库中的内容相关时，主动使用知识库检索工具
2. 如果从知识库中找到相关信息，请在回答中使用引用标记[1][2][3]等
3. 如果知识库中没有相关信息，可以基于自身知识回答
4. 始终保持友好、专业的态度
5. 回答要简洁明了，重点突出

## 引用格式（非常重要）：
- 知识库返回的内容会用[1][2][3]等序号标记来源
- 你的回答中引用知识库信息时，在相关内容后加上对应的引用标记，例如：根据课程要求[1]，需要提交源代码[2]。
- 只需用自己的话总结信息，并在适当位置添加引用标记[数字]

## 回答格式：
- 直接用自己的语言组织答案，不要复制粘贴知识库内容
- 使用清晰的结构（可使用Markdown格式）
- 对于复杂问题，可以分点回答
- 引用知识库时只使用[1][2]等标记，不显示来源文件名
"""


class AgentService_lyl:
    """Agent服务类 - 使用LangChain v1.0的create_agent，支持流式输出_lyl"""

    def __init__(self):
        """初始化Agent服务_lyl"""
        self._agent = None
        self._model = None
        log_lyl.info("AgentService 初始化完成")

    def get_model_lyl(self) -> ChatOpenAI:
        """获取LLM模型实例_lyl"""
        if self._model is None:
            log_lyl.info("正在创建 DeepSeek 模型实例...")
            self._model = ChatOpenAI(
                model="deepseek-chat",
                api_key=settings.DEEPSEEK_API_KEY,
                base_url=settings.DEEPSEEK_BASE_URL,
                temperature=0.7,
            )
            log_lyl.success("DeepSeek 模型实例创建成功")
        return self._model

    def create_agent_lyl(self):
        """创建Agent实例 - 使用LangChain v1.0的create_agent_lyl"""
        if self._agent is None:
            log_lyl.info("正在创建 Agent 实例...")
            model = self.get_model_lyl()
            tools = get_rag_tools_lyl()
            log_lyl.debug(f"加载了 {len(tools)} 个工具")

            # 使用LangChain v1.0的create_agent
            self._agent = create_agent(
                model=model,
                tools=tools,
                system_prompt=SYSTEM_PROMPT_LYL,
            )
            log_lyl.success("Agent 实例创建成功")

        return self._agent

    def format_history_messages_lyl(
        self,
        history: Optional[List[Dict[str, str]]] = None
    ) -> List[Dict[str, str]]:
        """格式化历史消息为LangChain v1.0格式_lyl"""
        if not history:
            return []

        messages = []
        for msg in history:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        return messages

    async def chat_stream_lyl(
        self,
        message: str,
        history: Optional[List[Dict[str, str]]] = None,
        use_knowledge_base: bool = True
    ) -> AsyncGenerator[str, None]:
        """
        流式对话 - 使用astream_events区分模型输出和工具输出_lyl

        Yields:
            SSE格式的数据块
        """
        log_lyl.info(f"开始流式对话，消息长度: {len(message)}，使用知识库: {use_knowledge_base}")

        # 清空上次的来源记录
        clear_sources_lyl()

        try:
            agent = self.create_agent_lyl()

            # 构建消息列表：历史消息 + 当前消息
            messages = self.format_history_messages_lyl(history)
            messages.append({"role": "user", "content": message})
            log_lyl.debug(f"消息历史数量: {len(messages) - 1}")

            full_content = ""
            tool_call_id = 0  # 工具调用计数器

            # 使用astream_events区分模型输出和工具调用
            log_lyl.info("开始流式获取 AI 回复 (astream_events)...")
            async for event in agent.astream_events(
                {"messages": messages},
                version="v2"
            ):
                event_type = event.get("event", "")

                # 只处理模型的流式输出，忽略工具返回的内容
                if event_type == "on_chat_model_stream":
                    chunk = event.get("data", {}).get("chunk")
                    if chunk:
                        content = self.extract_token_content_lyl(chunk)
                        if content:
                            full_content += content
                            event_data = {
                                "type": "token",
                                "content": content
                            }
                            yield f"data: {json.dumps(event_data, ensure_ascii=False)}\n\n"

                # 工具开始调用 - 将工具调用标记嵌入到内容流中
                elif event_type == "on_tool_start":
                    tool_name = event.get("name", "")
                    tool_input = event.get("data", {}).get("input", {})
                    tool_call_id += 1
                    log_lyl.info(f"工具开始调用: {tool_name}, 参数: {tool_input}")

                    # 生成工具调用标记，嵌入到内容中
                    tool_args_json = json.dumps(tool_input, ensure_ascii=False)
                    tool_marker = f"\n[[TOOL:{tool_call_id}:{tool_name}:running:{tool_args_json}]]\n"
                    full_content += tool_marker

                    event_data = {
                        "type": "token",
                        "content": tool_marker
                    }
                    yield f"data: {json.dumps(event_data, ensure_ascii=False)}\n\n"

                # 工具调用结束 - 发送结束标记，更新工具状态
                elif event_type == "on_tool_end":
                    tool_name = event.get("name", "")
                    log_lyl.info(f"工具调用结束: {tool_name}")

                    # 发送工具完成标记
                    tool_end_marker = f"[[TOOL_END:{tool_call_id}:{tool_name}]]"
                    full_content += tool_end_marker

                    event_data = {
                        "type": "token",
                        "content": tool_end_marker
                    }
                    yield f"data: {json.dumps(event_data, ensure_ascii=False)}\n\n"

            # 获取检索的来源信息
            sources = get_last_sources_lyl()
            if sources:
                log_lyl.info(f"返回 {len(sources)} 个引用来源")
                sources_event = {
                    "type": "sources",
                    "sources": sources
                }
                yield f"data: {json.dumps(sources_event, ensure_ascii=False)}\n\n"

            # 发送完成事件
            log_lyl.success(f"流式对话完成，响应长度: {len(full_content)}")
            done_event = {
                "type": "done",
                "full_content": full_content,
                "has_sources": len(sources) > 0
            }
            yield f"data: {json.dumps(done_event, ensure_ascii=False)}\n\n"

        except Exception as e:
            log_lyl.error(f"流式对话发生错误: {str(e)}")
            error_event = {
                "type": "error",
                "message": f"处理请求时发生错误: {str(e)}"
            }
            yield f"data: {json.dumps(error_event, ensure_ascii=False)}\n\n"

    def extract_token_content_lyl(self, token: Any) -> str:
        """从token中提取文本内容_lyl"""
        # 尝试不同的属性获取内容
        if hasattr(token, 'content'):
            content = token.content
            if isinstance(content, str):
                return content
            elif isinstance(content, list):
                # content_blocks格式
                texts = []
                for block in content:
                    if isinstance(block, dict) and 'text' in block:
                        texts.append(block['text'])
                    elif hasattr(block, 'text'):
                        texts.append(block.text)
                return ''.join(texts)
        elif hasattr(token, 'text'):
            return token.text
        elif hasattr(token, 'content_blocks'):
            texts = []
            for block in token.content_blocks:
                if hasattr(block, 'text'):
                    texts.append(block.text)
            return ''.join(texts)
        return ""

    def extract_response_content_lyl(self, message: Any) -> str:
        """从消息对象中提取响应内容_lyl"""
        if hasattr(message, 'content'):
            return message.content
        elif hasattr(message, 'text'):
            return message.text
        elif isinstance(message, dict):
            return message.get('content', str(message))
        else:
            return str(message)

    def extract_sources_lyl(self, result: Dict) -> Optional[List[str]]:
        """从结果中提取引用来源_lyl"""
        sources = []
        if "messages" in result:
            for msg in result["messages"]:
                if hasattr(msg, 'name') and msg.name == "knowledge_base_search_lyl":
                    content = getattr(msg, 'content', '')
                    if "来源" in content:
                        sources.append(content)
        return sources if sources else None


# 全局实例
agent_service = AgentService_lyl()

