/**
 * 类型定义_lyl
 */

export type Message_lyl = {
  id?: number;
  role: 'user' | 'assistant';
  content: string;
  created_at?: string;
  sources?: Source_lyl[];  // AI回复时的引用来源
};

export type Source_lyl = {
  id: number;
  source: string;
  content: string;
};

export type Conversation_lyl = {
  id: number;
  title: string;
  created_at: string;
  updated_at: string;
  messages?: Message_lyl[];
};

export type Document_lyl = {
  id: number;
  filename: string;
  file_type: string;
  file_size: number;
  chunk_count: number;
  created_at: string;
};

export type KnowledgeStats_lyl = {
  total_documents: number;
  total_chunks: number;
  file_types: Record<string, number>;
};

export type SearchResult_lyl = {
  content: string;
  metadata: {
    source: string;
    chunk_index: number;
  };
  score: number;
};

/**
 * 工具调用类型_lyl
 */
export type ToolCall_lyl = {
  id: string;
  name: string;
  args?: Record<string, unknown>;
  status: 'running' | 'completed';
};

