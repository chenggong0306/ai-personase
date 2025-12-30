/**
 * 对话列表组件_lyl
 */
import React from 'react';
import { List, Button, Popconfirm, Empty } from 'antd';
import { MessageOutlined, DeleteOutlined, PlusOutlined } from '@ant-design/icons';
import type { Conversation_lyl } from '../types/index_lyl';
import './ConversationList_lyl.css';

interface Props {
  conversations: Conversation_lyl[];
  currentId?: number;
  onSelect_lyl: (id: number) => void;
  onDelete_lyl: (id: number) => void;
  onCreate_lyl: () => void;
  loading?: boolean;
}

const ConversationList_lyl: React.FC<Props> = ({
  conversations,
  currentId,
  onSelect_lyl,
  onDelete_lyl,
  onCreate_lyl,
  loading = false,
}) => {
  return (
    <div className="conversation-list_lyl">
      <div className="list-header_lyl">
        <h3>对话历史</h3>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={onCreate_lyl}
          size="small"
        >
          新对话
        </Button>
      </div>
      
      {conversations.length === 0 ? (
        <Empty description="暂无对话" className="empty-list_lyl" />
      ) : (
        <List
          loading={loading}
          dataSource={conversations}
          renderItem={(item) => (
            <List.Item
              className={`conversation-item_lyl ${item.id === currentId ? 'active' : ''}`}
              onClick={() => onSelect_lyl(item.id)}
              actions={[
                <Popconfirm
                  key="delete"
                  title="确定删除此对话？"
                  onConfirm={(e) => {
                    e?.stopPropagation();
                    onDelete_lyl(item.id);
                  }}
                  okText="确定"
                  cancelText="取消"
                >
                  <Button
                    type="text"
                    danger
                    icon={<DeleteOutlined />}
                    size="small"
                    onClick={(e) => e.stopPropagation()}
                  />
                </Popconfirm>,
              ]}
            >
              <List.Item.Meta
                avatar={<MessageOutlined className="conversation-icon_lyl" />}
                title={item.title || '新对话'}
                description={new Date(item.updated_at).toLocaleString()}
              />
            </List.Item>
          )}
        />
      )}
    </div>
  );
};

export default ConversationList_lyl;

