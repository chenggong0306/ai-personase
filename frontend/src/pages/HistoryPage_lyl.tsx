/**
 * 对话历史页面_lyl - 点击查看跳转到聊天页面继续对话
 */
import React, { useState, useEffect } from 'react';
import { List, Card, Button, Empty, Popconfirm, message as antMessage, Input } from 'antd';
import { MessageOutlined, DeleteOutlined, SearchOutlined, EyeOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import type { Conversation_lyl } from '../types/index_lyl';
import { getConversations_lyl, deleteConversation_lyl } from '../services/api_lyl';
import './HistoryPage_lyl.css';

const { Search } = Input;

const HistoryPage_lyl: React.FC = () => {
  const navigate = useNavigate();
  const [conversations, setConversations] = useState<Conversation_lyl[]>([]);
  const [filteredConversations, setFilteredConversations] = useState<Conversation_lyl[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchText, setSearchText] = useState('');

  // 加载对话列表_lyl
  const loadConversations_lyl = async () => {
    setLoading(true);
    try {
      const data = await getConversations_lyl();
      setConversations(data);
      setFilteredConversations(data);
    } catch (error) {
      antMessage.error('加载对话历史失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadConversations_lyl();
  }, []);

  // 搜索过滤_lyl
  const handleSearch_lyl = (value: string) => {
    setSearchText(value);
    if (!value.trim()) {
      setFilteredConversations(conversations);
    } else {
      const filtered = conversations.filter(c =>
        c.title?.toLowerCase().includes(value.toLowerCase())
      );
      setFilteredConversations(filtered);
    }
  };

  // 删除对话_lyl
  const handleDelete_lyl = async (id: number) => {
    try {
      await deleteConversation_lyl(id);
      antMessage.success('对话已删除');
      loadConversations_lyl();
    } catch (error) {
      antMessage.error('删除失败');
    }
  };

  // 查看对话 - 跳转到聊天页面继续对话_lyl
  const handleView_lyl = (conversation: Conversation_lyl) => {
    navigate(`/?conversation_id=${conversation.id}`);
  };

  return (
    <div className="history-page_lyl">
      <div className="page-header_lyl">
        <h2>📜 对话历史</h2>
        <Search
          placeholder="搜索对话..."
          allowClear
          onSearch={handleSearch_lyl}
          onChange={(e) => handleSearch_lyl(e.target.value)}
          style={{ width: 300 }}
          prefix={<SearchOutlined />}
        />
      </div>

      <Card className="history-card_lyl">
        {filteredConversations.length === 0 ? (
          <Empty description={searchText ? '未找到匹配的对话' : '暂无对话历史'} />
        ) : (
          <List
            loading={loading}
            dataSource={filteredConversations}
            pagination={{ pageSize: 10, showTotal: (total) => `共 ${total} 条对话` }}
            renderItem={(item) => (
              <List.Item
                className="history-item_lyl"
                actions={[
                  <Button key="view" type="link" icon={<EyeOutlined />} onClick={() => handleView_lyl(item)}>
                    继续对话
                  </Button>,
                  <Popconfirm
                    key="delete"
                    title="确定删除此对话？"
                    onConfirm={() => handleDelete_lyl(item.id)}
                    okText="确定"
                    cancelText="取消"
                  >
                    <Button type="link" danger icon={<DeleteOutlined />}>删除</Button>
                  </Popconfirm>,
                ]}
              >
                <List.Item.Meta
                  avatar={<MessageOutlined className="history-icon_lyl" />}
                  title={item.title || '新对话'}
                  description={`创建于 ${new Date(item.created_at).toLocaleString()} · 更新于 ${new Date(item.updated_at).toLocaleString()}`}
                />
              </List.Item>
            )}
          />
        )}
      </Card>
    </div>
  );
};

export default HistoryPage_lyl;

