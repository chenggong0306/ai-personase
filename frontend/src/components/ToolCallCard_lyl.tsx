/**
 * 工具调用卡片组件_lyl
 * 显示AI正在调用的工具信息
 */
import React, { useState } from 'react';
import { ToolOutlined, CheckCircleOutlined, LoadingOutlined, DownOutlined, RightOutlined } from '@ant-design/icons';
import type { ToolCall_lyl } from '../types/index_lyl';
import './ToolCallCard_lyl.css';

interface ToolCallCardProps_lyl {
  toolCall: ToolCall_lyl;
}

// 工具名称映射
const toolNameMap: Record<string, string> = {
  'search_knowledge': '知识库检索',
  'rag_search': '知识库检索',
  'search_knowledge_base': '知识库检索',
};

const ToolCallCard_lyl: React.FC<ToolCallCardProps_lyl> = ({ toolCall }) => {
  const [expanded, setExpanded] = useState(false);

  const displayName = toolNameMap[toolCall.name] || toolCall.name;
  const isRunning = toolCall.status === 'running';

  // 提取关键参数显示_lyl
  const getArgsPreview_lyl = () => {
    if (!toolCall.args) return null;
    const query = toolCall.args.query || toolCall.args.question || toolCall.args.keyword;
    if (query) {
      return <span className="tool-args-preview_lyl">查询: "{String(query)}"</span>;
    }
    return null;
  };

  return (
    <div className={`tool-call-card_lyl ${isRunning ? 'running' : 'completed'}`}>
      <div className="tool-call-header_lyl" onClick={() => setExpanded(!expanded)}>
        <div className="tool-call-icon_lyl">
          <ToolOutlined />
        </div>
        <div className="tool-call-info_lyl">
          <span className="tool-call-name_lyl">{displayName}</span>
          {getArgsPreview_lyl()}
        </div>
        <div className="tool-call-status_lyl">
          {isRunning ? (
            <LoadingOutlined spin className="status-running_lyl" />
          ) : (
            <CheckCircleOutlined className="status-completed_lyl" />
          )}
          {toolCall.args && (
            <span className="expand-icon_lyl">
              {expanded ? <DownOutlined /> : <RightOutlined />}
            </span>
          )}
        </div>
      </div>
      {expanded && toolCall.args && (
        <div className="tool-call-detail_lyl">
          <pre>{JSON.stringify(toolCall.args, null, 2)}</pre>
        </div>
      )}
    </div>
  );
};

export default ToolCallCard_lyl;

