/**
 * 知识库管理页面_lyl
 */
import React, { useState, useEffect } from 'react';
import { Table, Button, Upload, Card, Statistic, Row, Col, message as antMessage, Popconfirm, Tag } from 'antd';
import { UploadOutlined, DeleteOutlined, FileTextOutlined, DatabaseOutlined, ReloadOutlined } from '@ant-design/icons';
import type { UploadProps } from 'antd';
import type { Document_lyl, KnowledgeStats_lyl } from '../types/index_lyl';
import { getDocuments_lyl, uploadDocument_lyl, deleteDocument_lyl, getKnowledgeStats_lyl } from '../services/api_lyl';
import './KnowledgePage_lyl.css';

const KnowledgePage_lyl: React.FC = () => {
  const [documents, setDocuments] = useState<Document_lyl[]>([]);
  const [stats, setStats] = useState<KnowledgeStats_lyl | null>(null);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);

  // 加载数据_lyl
  const loadData_lyl = async () => {
    setLoading(true);
    try {
      const [docs, statsData] = await Promise.all([
        getDocuments_lyl(),
        getKnowledgeStats_lyl(),
      ]);
      setDocuments(docs.documents || []);
      setStats(statsData);
    } catch (error) {
      antMessage.error('加载数据失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData_lyl();
  }, []);

  // 上传配置_lyl
  const uploadProps_lyl: UploadProps = {
    beforeUpload: async (file) => {
      setUploading(true);
      try {
        await uploadDocument_lyl(file);
        antMessage.success(`${file.name} 上传成功`);
        loadData_lyl();
      } catch (error: any) {
        antMessage.error(error.response?.data?.detail || '上传失败');
      } finally {
        setUploading(false);
      }
      return false;
    },
    showUploadList: false,
    accept: '.txt,.md,.pdf,.docx,.doc',
  };

  // 删除文档_lyl
  const handleDelete_lyl = async (id: number) => {
    try {
      await deleteDocument_lyl(id);
      antMessage.success('文档已删除');
      loadData_lyl();
    } catch (error) {
      antMessage.error('删除失败');
    }
  };

  // 格式化文件大小_lyl
  const formatFileSize_lyl = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  // 获取文件类型颜色_lyl
  const getFileTypeColor_lyl = (type: string) => {
    const colors: Record<string, string> = {
      txt: 'blue', md: 'green', pdf: 'red', docx: 'purple', doc: 'purple',
    };
    return colors[type] || 'default';
  };

  const columns_lyl = [
    { title: '文件名', dataIndex: 'filename', key: 'filename', ellipsis: true },
    {
      title: '类型', dataIndex: 'file_type', key: 'file_type', width: 80,
      render: (type: string) => <Tag color={getFileTypeColor_lyl(type)}>{type.toUpperCase()}</Tag>,
    },
    { title: '大小', dataIndex: 'file_size', key: 'file_size', width: 100, render: formatFileSize_lyl },
    { title: '分块数', dataIndex: 'chunk_count', key: 'chunk_count', width: 80 },
    {
      title: '上传时间', dataIndex: 'created_at', key: 'created_at', width: 180,
      render: (time: string) => new Date(time).toLocaleString(),
    },
    {
      title: '操作', key: 'action', width: 80,
      render: (_: any, record: Document_lyl) => (
        <Popconfirm title="确定删除此文档？" onConfirm={() => handleDelete_lyl(record.id)} okText="确定" cancelText="取消">
          <Button type="text" danger icon={<DeleteOutlined />} size="small" />
        </Popconfirm>
      ),
    },
  ];

  return (
    <div className="knowledge-page_lyl">
      <div className="page-header_lyl">
        <h2>📚 知识库管理</h2>
        <div>
          <Button icon={<ReloadOutlined />} onClick={loadData_lyl} style={{ marginRight: 12 }}>刷新</Button>
          <Upload {...uploadProps_lyl}>
            <Button type="primary" icon={<UploadOutlined />} loading={uploading}>上传文档</Button>
          </Upload>
        </div>
      </div>

      <Row gutter={16} className="stats-row_lyl">
        <Col span={8}>
          <Card><Statistic title="文档总数" value={stats?.total_documents || 0} prefix={<FileTextOutlined />} /></Card>
        </Col>
        <Col span={8}>
          <Card><Statistic title="文本块总数" value={stats?.total_chunks || 0} prefix={<DatabaseOutlined />} /></Card>
        </Col>
        <Col span={8}>
          <Card>
            <div className="file-types_lyl">
              <div className="stat-title">文件类型分布</div>
              <div className="tags-container">{stats?.file_types && Object.entries(stats.file_types).map(([type, count]) => (
                <Tag key={type} color={getFileTypeColor_lyl(type)}>{type}: {count}</Tag>
              ))}</div>
            </div>
          </Card>
        </Col>
      </Row>

      <Card className="table-card_lyl">
        <Table columns={columns_lyl} dataSource={documents} rowKey="id" loading={loading} pagination={{ pageSize: 10 }}
          locale={{ emptyText: '暂无文档，请上传文件' }} />
      </Card>
    </div>
  );
};

export default KnowledgePage_lyl;

