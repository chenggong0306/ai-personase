/**
 * API服务层 - 与后端通信_lyl
 */
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ==================== 对话相关API ====================

/** 获取所有对话列表_lyl */
export const getConversations_lyl = async () => {
  const response = await api.get('/chat/conversations');
  return response.data.conversations;
};

/** 创建新对话_lyl */
export const createConversation_lyl = async (title?: string) => {
  const response = await api.post('/chat/conversations', { title });
  return response.data;
};

/** 获取对话详情_lyl */
export const getConversation_lyl = async (conversationId: number) => {
  const response = await api.get(`/chat/conversations/${conversationId}`);
  return response.data;
};

/** 删除对话_lyl */
export const deleteConversation_lyl = async (conversationId: number) => {
  const response = await api.delete(`/chat/conversations/${conversationId}`);
  return response.data;
};

/** 获取对话消息_lyl */
export const getConversationMessages_lyl = async (conversationId: number) => {
  const response = await api.get(`/chat/conversations/${conversationId}/messages`);
  return response.data.messages;
};

import type { Source_lyl } from '../types/index_lyl';

/** 发送消息（SSE流式）_lyl */
export const sendMessageStream_lyl = async (
  message: string,
  conversationId?: number,
  useKnowledgeBase: boolean = true,
  onToken: (token: string) => void = () => {},
  onDone: (fullContent: string, convId: number, sources: Source_lyl[]) => void = () => {},
  onError: (error: string) => void = () => {},
  onSources: (sources: Source_lyl[]) => void = () => {}
) => {
  const response = await fetch(`${API_BASE_URL}/chat/send/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message,
      conversation_id: conversationId,
      use_knowledge_base: useKnowledgeBase,
    }),
  });

  const reader = response.body?.getReader();
  const decoder = new TextDecoder();
  let currentConversationId = conversationId;
  let currentSources: Source_lyl[] = [];

  if (!reader) {
    onError('无法获取响应流');
    return;
  }

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const text = decoder.decode(value);
    const lines = text.split('\n');

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        try {
          const data = JSON.parse(line.slice(6));

          if (data.type === 'init') {
            currentConversationId = data.conversation_id;
          } else if (data.type === 'token') {
            // token已包含工具调用标记，直接传递
            onToken(data.content);
          } else if (data.type === 'sources') {
            currentSources = data.sources || [];
            onSources(currentSources);
          } else if (data.type === 'done') {
            onDone(data.full_content, currentConversationId!, currentSources);
          } else if (data.type === 'error') {
            onError(data.message);
          }
        } catch (e) {
          // 忽略解析错误
        }
      }
    }
  }
};

// ==================== 知识库相关API ====================

/** 获取所有文档_lyl */
export const getDocuments_lyl = async () => {
  const response = await api.get('/knowledge/documents');
  return response.data;
};

/** 上传文档_lyl */
export const uploadDocument_lyl = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post('/knowledge/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};

/** 删除文档_lyl */
export const deleteDocument_lyl = async (documentId: number) => {
  const response = await api.delete(`/knowledge/documents/${documentId}`);
  return response.data;
};

/** 搜索知识库_lyl */
export const searchKnowledge_lyl = async (query: string, k: number = 5) => {
  const response = await api.get('/knowledge/search', {
    params: { query, k },
  });
  return response.data;
};

/** 获取知识库统计_lyl */
export const getKnowledgeStats_lyl = async () => {
  const response = await api.get('/knowledge/stats');
  return response.data;
};

export default api;

