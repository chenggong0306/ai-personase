/**
 * Loading动画组件_lyl - 三个圆点跳动效果
 */
import React from 'react';
import { Avatar } from 'antd';
import { RobotOutlined } from '@ant-design/icons';
import './LoadingDots_lyl.css';

const LoadingDots_lyl: React.FC = () => {
  return (
    <div className="chat-message_lyl assistant loading-message_lyl">
      <Avatar
        icon={<RobotOutlined />}
        className="avatar_lyl assistant-avatar"
      />
      <div className="message-content_lyl assistant-content loading-content_lyl">
        <div className="loading-dots_lyl">
          <span className="dot_lyl"></span>
          <span className="dot_lyl"></span>
          <span className="dot_lyl"></span>
        </div>
      </div>
    </div>
  );
};

export default LoadingDots_lyl;

