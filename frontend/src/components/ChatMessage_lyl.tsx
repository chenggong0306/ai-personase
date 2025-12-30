/**
 * 聊天消息组件_lyl - 支持引用标记点击和工具调用卡片
 */
import React, { useMemo } from 'react';
import { Avatar } from 'antd';
import { UserOutlined, RobotOutlined } from '@ant-design/icons';
import type { Message_lyl } from '../types/index_lyl';
import ToolCallCard_lyl from './ToolCallCard_lyl';
import type { ToolCall_lyl } from '../types/index_lyl';
import './ChatMessage_lyl.css';

interface Props {
  message: Message_lyl;
  onSourceClick_lyl?: (sourceId: number) => void;
}

// 解析工具调用标记的类型
interface ContentBlock_lyl {
  type: 'text' | 'tool';
  content?: string;
  toolCall?: ToolCall_lyl;
}

const ChatMessage_lyl: React.FC<Props> = ({ message, onSourceClick_lyl }) => {
  const isUser = message.role === 'user';

  // 解析内容，提取工具调用标记和普通文本_lyl
  const parseContent_lyl = (content: string): ContentBlock_lyl[] => {
    const blocks: ContentBlock_lyl[] = [];

    // 匹配工具调用标记: [[TOOL:id:name:status:args]] 和 [[TOOL_END:id:name]]
    const toolEndRegex = /\[\[TOOL_END:(\d+):([^\]]+)\]\]/g;

    // 记录每个工具的状态
    const toolStatuses: Record<string, 'running' | 'completed'> = {};

    // 先扫描所有TOOL_END标记来确定完成状态
    let endMatch;
    while ((endMatch = toolEndRegex.exec(content)) !== null) {
      const toolId = endMatch[1];
      toolStatuses[toolId] = 'completed';
    }

    // 移除TOOL_END标记
    let cleanedContent = content.replace(toolEndRegex, '');

    // 分割并解析内容
    let lastIndex = 0;
    let match;
    const regex = /\[\[TOOL:(\d+):([^:]+):(running|completed):(.+?)\]\]/g;

    while ((match = regex.exec(cleanedContent)) !== null) {
      // 添加标记之前的文本
      if (match.index > lastIndex) {
        const text = cleanedContent.slice(lastIndex, match.index).trim();
        if (text) {
          blocks.push({ type: 'text', content: text });
        }
      }

      // 添加工具调用块
      const toolId = match[1];
      const toolName = match[2];
      const status = toolStatuses[toolId] || match[3];
      let args = {};
      try {
        args = JSON.parse(match[4]);
      } catch {
        // 解析失败则忽略
      }

      blocks.push({
        type: 'tool',
        toolCall: {
          id: `tool_${toolId}`,
          name: toolName,
          args: args as Record<string, unknown>,
          status: status as 'running' | 'completed'
        }
      });

      lastIndex = match.index + match[0].length;
    }

    // 添加剩余文本
    if (lastIndex < cleanedContent.length) {
      const text = cleanedContent.slice(lastIndex).trim();
      if (text) {
        blocks.push({ type: 'text', content: text });
      }
    }

    // 如果没有找到任何块，返回原始内容
    if (blocks.length === 0 && content.trim()) {
      blocks.push({ type: 'text', content: content });
    }

    return blocks;
  };

  // 将[1][2]等引用标记转换为可点击元素_lyl
  const renderTextWithRefs_lyl = (text: string) => {
    const parts = text.split(/(\[\d+\])/g);

    return parts.map((part, index) => {
      const match = part.match(/^\[(\d+)\]$/);
      if (match) {
        const sourceId = parseInt(match[1], 10);
        return (
          <span
            key={index}
            className="source-ref_lyl"
            onClick={() => onSourceClick_lyl?.(sourceId)}
            title={`查看引用来源 [${sourceId}]`}
          >
            [{sourceId}]
          </span>
        );
      }
      return part;
    });
  };

  // 解析后的内容块
  const contentBlocks = useMemo(() => {
    if (isUser) return [{ type: 'text' as const, content: message.content }];
    return parseContent_lyl(message.content);
  }, [message.content, isUser]);

  return (
    <div className={`chat-message_lyl ${isUser ? 'user' : 'assistant'}`}>
      <Avatar
        icon={isUser ? <UserOutlined /> : <RobotOutlined />}
        className={`avatar_lyl ${isUser ? 'user-avatar' : 'assistant-avatar'}`}
      />
      <div className={`message-content_lyl ${isUser ? 'user-content' : 'assistant-content'}`}>
        {contentBlocks.map((block, index) => {
          if (block.type === 'tool' && block.toolCall) {
            return <ToolCallCard_lyl key={index} toolCall={block.toolCall} />;
          }
          return (
            <div key={index} className="message-text_lyl">
              {renderTextWithRefs_lyl(block.content || '')}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default ChatMessage_lyl;

