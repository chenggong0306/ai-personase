/**
 * 聊天页面_lyl - 支持从历史记录加载对话并继续聊天
 */
import React, { useState, useEffect, useRef } from 'react';
import { message as antMessage, Card, Empty, Drawer, Button } from 'antd';
import { FileTextOutlined, PlusOutlined } from '@ant-design/icons';
import { useSearchParams } from 'react-router-dom';
import ChatMessage_lyl from '../components/ChatMessage_lyl';
import ChatInput_lyl from '../components/ChatInput_lyl';
import LoadingDots_lyl from '../components/LoadingDots_lyl';
import type { Message_lyl, Source_lyl } from '../types/index_lyl';
import { sendMessageStream_lyl, getConversationMessages_lyl } from '../services/api_lyl';
import './ChatPage_lyl.css';

const ChatPage_lyl: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [currentConversationId, setCurrentConversationId] = useState<number | undefined>();
  const [messages, setMessages] = useState<Message_lyl[]>([]);
  const [streaming, setStreaming] = useState(false);
  const [streamingContent, setStreamingContent] = useState('');
  const [currentSources, setCurrentSources] = useState<Source_lyl[]>([]);
  const [highlightedSourceId, setHighlightedSourceId] = useState<number | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // 从URL参数加载历史对话_lyl
  useEffect(() => {
    const conversationIdParam = searchParams.get('conversation_id');
    if (conversationIdParam) {
      const convId = parseInt(conversationIdParam, 10);
      if (!isNaN(convId)) {
        loadConversationHistory_lyl(convId);
      }
    }
  }, [searchParams]);

  // 加载对话历史消息_lyl
  const loadConversationHistory_lyl = async (convId: number) => {
    setLoadingHistory(true);
    try {
      const historyMessages = await getConversationMessages_lyl(convId);
      setMessages(historyMessages);
      setCurrentConversationId(convId);
    } catch (error) {
      antMessage.error('加载对话历史失败');
    } finally {
      setLoadingHistory(false);
    }
  };

  // 开始新对话_lyl
  const handleNewConversation_lyl = () => {
    setMessages([]);
    setCurrentConversationId(undefined);
    setCurrentSources([]);
    setSearchParams({});
  };

  // 滚动到底部_lyl
  const scrollToBottom_lyl = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom_lyl();
  }, [messages, streamingContent]);

  // 处理引用点击_lyl - 打开抽屉并高亮对应来源
  const handleSourceClick_lyl = (sourceId: number) => {
    setHighlightedSourceId(sourceId);
    setDrawerOpen(true);
    // 3秒后取消高亮
    setTimeout(() => setHighlightedSourceId(null), 3000);
  };

  // 发送消息_lyl
  const handleSendMessage_lyl = async (content: string, useKnowledgeBase: boolean) => {
    const userMessage: Message_lyl = { role: 'user', content };
    setMessages((prev) => [...prev, userMessage]);
    setStreaming(true);
    setStreamingContent('');
    setCurrentSources([]);

    await sendMessageStream_lyl(
      content,
      currentConversationId,
      useKnowledgeBase,
      (token) => {
        // token已经包含工具调用标记，直接追加
        setStreamingContent((prev) => prev + token);
      },
      (fullContent, convId, sources) => {
        setStreaming(false);
        setStreamingContent('');
        const assistantMessage: Message_lyl = {
          role: 'assistant',
          content: fullContent,
          sources: sources
        };
        setMessages((prev) => [...prev, assistantMessage]);
        if (!currentConversationId) {
          setCurrentConversationId(convId);
        }
      },
      (error) => {
        setStreaming(false);
        setStreamingContent('');
        antMessage.error(error);
      },
      (sources) => {
        setCurrentSources(sources);
      }
    );
  };

  // 获取当前要显示的来源（流式时用currentSources，否则用最后一条消息的sources）
  const displaySources_lyl = streaming
    ? currentSources
    : (messages.length > 0 && messages[messages.length - 1].role === 'assistant'
        ? messages[messages.length - 1].sources || []
        : []);

  return (
    <div className="chat-page_lyl">
      {/* 聊天区域 */}
      <div className="chat-main_lyl full-width">
        <div className="chat-header_lyl">
          <h2>💬 智能知识助手 - 小知</h2>
          {currentConversationId && (
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={handleNewConversation_lyl}
              className="new-chat-btn_lyl"
            >
              新对话
            </Button>
          )}
        </div>
        <div className="messages-container_lyl">
          {loadingHistory && (
            <div className="loading-history_lyl">
              <LoadingDots_lyl />
              <span>加载对话历史中...</span>
            </div>
          )}
          {!loadingHistory && messages.length === 0 && !streaming && (
            <div className="welcome-message_lyl">
              <h3>👋 你好！我是小知</h3>
              <p>我是您的个人知识助手，可以帮您回答问题并从知识库中检索相关信息。</p>
              <p>试着问我一些问题吧！</p>
            </div>
          )}
          {messages.map((msg, index) => (
            <ChatMessage_lyl
              key={index}
              message={msg}
              onSourceClick_lyl={handleSourceClick_lyl}
            />
          ))}
          {/* 流式输出时显示 - 工具调用标记已嵌入content中 */}
          {streaming && !streamingContent && (
            <LoadingDots_lyl />
          )}
          {streaming && streamingContent && (
            <ChatMessage_lyl
              message={{ role: 'assistant', content: streamingContent + '▌' }}
              onSourceClick_lyl={handleSourceClick_lyl}
            />
          )}
          <div ref={messagesEndRef} />
        </div>
        <ChatInput_lyl
          onSend_lyl={handleSendMessage_lyl}
          disabled={false}
          loading={streaming}
        />
      </div>

      {/* 右侧抽屉 - 参考来源 */}
      <Drawer
        title={
          <span>
            <FileTextOutlined /> 参考来源 ({displaySources_lyl.length})
          </span>
        }
        placement="right"
        styles={{ wrapper: { width: 400 } }}
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        className="sources-drawer_lyl"
      >
        {displaySources_lyl.length === 0 ? (
          <Empty
            image={Empty.PRESENTED_IMAGE_SIMPLE}
            description="暂无引用来源"
          />
        ) : (
          displaySources_lyl.map((source) => (
            <Card
              key={source.id}
              size="small"
              className={`source-card_lyl ${highlightedSourceId === source.id ? 'highlighted' : ''}`}
              title={
                <span className="source-title_lyl">
                  <span className="source-id_lyl">[{source.id}]</span>
                  {source.source}
                </span>
              }
              style={{ marginBottom: 12 }}
            >
              <div className="source-preview_lyl">
                {source.content}
              </div>
            </Card>
          ))
        )}
      </Drawer>
    </div>
  );
};

export default ChatPage_lyl;

