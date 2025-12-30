/**
 * 聊天输入组件_lyl
 */
import React, { useState } from 'react';
import { Input, Button, Switch, Space } from 'antd';
import { SendOutlined, BookOutlined } from '@ant-design/icons';
import './ChatInput_lyl.css';

const { TextArea } = Input;

interface Props {
  onSend_lyl: (message: string, useKnowledgeBase: boolean) => void;
  disabled?: boolean;
  loading?: boolean;
}

const ChatInput_lyl: React.FC<Props> = ({ onSend_lyl, disabled = false, loading = false }) => {
  const [message, setMessage] = useState('');
  const [useKnowledgeBase, setUseKnowledgeBase] = useState(true);

  const handleSend_lyl = () => {
    if (message.trim() && !disabled && !loading) {
      onSend_lyl(message.trim(), useKnowledgeBase);
      setMessage('');
    }
  };

  const handleKeyDown_lyl = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend_lyl();
    }
  };

  return (
    <div className="chat-input-container_lyl">
      <div className="input-options_lyl">
        <Space>
          <BookOutlined />
          <span>使用知识库</span>
          <Switch
            checked={useKnowledgeBase}
            onChange={setUseKnowledgeBase}
            size="small"
          />
        </Space>
      </div>
      <div className="input-row_lyl">
        <TextArea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown_lyl}
          placeholder="输入您的问题... (Shift+Enter换行)"
          autoSize={{ minRows: 1, maxRows: 4 }}
          disabled={disabled || loading}
          className="message-input_lyl"
        />
        <Button
          type="primary"
          icon={<SendOutlined />}
          onClick={handleSend_lyl}
          disabled={!message.trim() || disabled}
          loading={loading}
          className="send-button_lyl"
        >
          发送
        </Button>
      </div>
    </div>
  );
};

export default ChatInput_lyl;

