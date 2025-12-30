"""
聊天API路由 - 处理对话和消息相关的请求
支持SSE流式输出
"""
from typing import Optional
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from backend.app.core.logger import log_lyl
from backend.app.models.schemas import (
    ChatRequest_lyl,
    ChatResponse_lyl,
    Conversation_lyl,
    ConversationCreate_lyl,
    SuccessResponse_lyl,
)
from backend.app.services.conversation_service import conversation_service
from backend.app.services.agent_service import agent_service

router = APIRouter(prefix="/chat", tags=["对话"])


@router.post("/send/stream")
async def send_message_stream_lyl(request: ChatRequest_lyl):
    """
    发送消息并以SSE流式方式获取AI回复_lyl

    - 如果conversation_id为空，会自动创建新对话
    - 支持选择是否使用知识库
    - 返回SSE流式响应
    """
    log_lyl.info(f"收到流式聊天请求，conversation_id: {request.conversation_id}")
    try:
        conversation_id = request.conversation_id

        # 如果没有对话ID，创建新对话
        if conversation_id is None:
            log_lyl.info("创建新对话...")
            conversation = await conversation_service.create_conversation_lyl()
            conversation_id = conversation["id"]
            # 自动生成标题
            await conversation_service.auto_generate_title_lyl(
                conversation_id, request.message
            )
            log_lyl.info(f"新对话创建成功，ID: {conversation_id}")

        # 保存用户消息
        await conversation_service.add_message_lyl(
            conversation_id, "user", request.message
        )
        log_lyl.debug("用户消息已保存")

        # 获取历史消息作为上下文
        history = await conversation_service.get_recent_messages_lyl(
            conversation_id, limit=10
        )
        history_formatted = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in history[:-1]  # 排除刚添加的当前消息
        ]

        async def generate_stream_lyl():
            """生成SSE流_lyl"""
            import json

            # 先发送conversation_id
            init_event = {
                "type": "init",
                "conversation_id": conversation_id
            }
            yield f"data: {json.dumps(init_event, ensure_ascii=False)}\n\n"

            full_response = ""

            # 流式获取Agent回复
            async for chunk in agent_service.chat_stream_lyl(
                message=request.message,
                history=history_formatted,
                use_knowledge_base=request.use_knowledge_base
            ):
                yield chunk

                # 解析chunk以收集完整响应
                if chunk.startswith("data: "):
                    try:
                        data = json.loads(chunk[6:].strip())
                        if data.get("type") == "done":
                            full_response = data.get("full_content", "")
                    except:
                        pass

            # 保存AI回复到数据库
            if full_response:
                await conversation_service.add_message_lyl(
                    conversation_id, "assistant", full_response
                )
                log_lyl.info(f"AI回复已保存，长度: {len(full_response)}")

        log_lyl.info("返回SSE流式响应")
        return StreamingResponse(
            generate_stream_lyl(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            }
        )

    except Exception as e:
        log_lyl.error(f"流式聊天请求处理失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send", response_model=ChatResponse_lyl)
async def send_message_lyl(request: ChatRequest_lyl):
    """
    发送消息并获取AI回复（非流式）_lyl

    - 如果conversation_id为空，会自动创建新对话
    - 支持选择是否使用知识库
    """
    try:
        conversation_id = request.conversation_id

        # 如果没有对话ID，创建新对话
        if conversation_id is None:
            conversation = await conversation_service.create_conversation_lyl()
            conversation_id = conversation["id"]
            # 自动生成标题
            await conversation_service.auto_generate_title_lyl(
                conversation_id, request.message
            )

        # 保存用户消息
        await conversation_service.add_message_lyl(
            conversation_id, "user", request.message
        )

        # 获取历史消息作为上下文
        history = await conversation_service.get_recent_messages_lyl(
            conversation_id, limit=10
        )
        history_formatted = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in history[:-1]  # 排除刚添加的当前消息
        ]

        # 使用流式方法收集完整响应
        full_response = ""
        import json
        async for chunk in agent_service.chat_stream_lyl(
            message=request.message,
            history=history_formatted,
            use_knowledge_base=request.use_knowledge_base
        ):
            if chunk.startswith("data: "):
                try:
                    data = json.loads(chunk[6:].strip())
                    if data.get("type") == "done":
                        full_response = data.get("full_content", "")
                except:
                    pass

        # 保存AI回复
        await conversation_service.add_message_lyl(
            conversation_id, "assistant", full_response
        )

        return ChatResponse_lyl(
            conversation_id=conversation_id,
            message=full_response,
            sources=None
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations")
async def get_conversations_lyl():
    """获取所有对话列表_lyl"""
    conversations = await conversation_service.get_all_conversations_lyl()
    return {"conversations": conversations}


@router.get("/conversations/{conversation_id}")
async def get_conversation_lyl(conversation_id: int):
    """获取单个对话详情（包含消息）_lyl"""
    conversation = await conversation_service.get_conversation_by_id_lyl(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="对话不存在")
    return conversation


@router.post("/conversations", response_model=dict)
async def create_conversation_lyl(data: ConversationCreate_lyl):
    """创建新对话_lyl"""
    conversation = await conversation_service.create_conversation_lyl(data.title)
    return conversation


@router.put("/conversations/{conversation_id}/title")
async def update_conversation_title_api_lyl(conversation_id: int, title: str):
    """更新对话标题_lyl"""
    await conversation_service.update_conversation_title_lyl(conversation_id, title)
    return SuccessResponse_lyl(message="标题更新成功")


@router.delete("/conversations/{conversation_id}")
async def delete_conversation_lyl(conversation_id: int):
    """删除对话_lyl"""
    await conversation_service.delete_conversation_lyl(conversation_id)
    return SuccessResponse_lyl(message="对话删除成功")


@router.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages_lyl(conversation_id: int):
    """获取对话的所有消息_lyl"""
    messages = await conversation_service.get_messages_by_conversation_id_lyl(conversation_id)
    return {"messages": messages}

