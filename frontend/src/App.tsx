/**
 * 主应用组件_lyl
 */
import { useState, useEffect } from 'react';
import { ConfigProvider, Layout, Menu } from 'antd';
import { MessageOutlined, BookOutlined, HistoryOutlined } from '@ant-design/icons';
import { useSearchParams } from 'react-router-dom';
import zhCN from 'antd/locale/zh_CN';
import ChatPage_lyl from './pages/ChatPage_lyl';
import KnowledgePage_lyl from './pages/KnowledgePage_lyl';
import HistoryPage_lyl from './pages/HistoryPage_lyl';
import './App.css';

const { Sider, Content } = Layout;

function App_lyl() {
  const [searchParams] = useSearchParams();
  const [currentPage, setCurrentPage] = useState<'chat' | 'knowledge' | 'history'>('chat');

  // 当URL有conversation_id参数时，自动切换到聊天页面_lyl
  useEffect(() => {
    const conversationId = searchParams.get('conversation_id');
    if (conversationId) {
      setCurrentPage('chat');
    }
  }, [searchParams]);

  const menuItems_lyl = [
    { key: 'chat', icon: <MessageOutlined />, label: '智能对话' },
    { key: 'knowledge', icon: <BookOutlined />, label: '知识库管理' },
    { key: 'history', icon: <HistoryOutlined />, label: '对话历史' },
  ];

  const renderPage_lyl = () => {
    switch (currentPage) {
      case 'chat':
        return <ChatPage_lyl />;
      case 'knowledge':
        return <KnowledgePage_lyl />;
      case 'history':
        return <HistoryPage_lyl />;
      default:
        return <ChatPage_lyl />;
    }
  };

  return (
    <ConfigProvider locale={zhCN}>
      <Layout className="app-layout_lyl">
        <Sider width={200} className="app-sider_lyl" theme="light">
          <div className="logo_lyl">
            <span className="logo-icon">🧠</span>
            <span className="logo-text">知识问答系统</span>
          </div>
          <Menu
            mode="inline"
            selectedKeys={[currentPage]}
            items={menuItems_lyl}
            onClick={({ key }) => setCurrentPage(key as 'chat' | 'knowledge' | 'history')}
            className="app-menu_lyl"
          />
        </Sider>
        <Content className="app-content_lyl">
          {renderPage_lyl()}
        </Content>
      </Layout>
    </ConfigProvider>
  );
}

export default App_lyl;
