export type QueryType = 'aggregation' | 'lookup' | 'multi_hop' | 'superlative' | 'temporal' | string;
export type PipelineKey = 'rag' | 'graphrag' | 'agent';

export interface TraceStep {
  step: number;
  action: string;
  tool: string;
  args: Record<string, any>;
  duration_s: number;
  tokens: number;
  observation?: string;
}

export interface PipelineResult {
  answer: string;
  correct: boolean;
  tokens: number;
  elapsed_time_s?: number;
  latency?: number;
  total_steps?: number;
  stopped_reason?: string;
  trace?: TraceStep[];
  citations?: string[];
}

export interface BenchmarkQuestion {
  question_id: string;
  query_type: QueryType;
  question: string;
  gold_answer: string[] | string;
  rag: PipelineResult;
  graphrag: PipelineResult;
  agent: PipelineResult;
  frac8?: number; // Captured candidate evidence fraction if applicable
}

export interface QueryTypeStats {
  total: number;
  accuracy: {
    rag: number;
    graphrag: number;
    agent: number;
  };
  tokens_avg: {
    rag: number;
    graphrag: number;
    agent: number;
  };
  latency_avg_s: {
    rag: number;
    graphrag: number;
    agent: number;
  };
  agent_avg_steps: number;
}

export interface BenchmarkSummary {
  benchmark_scale: string;
  timestamp: string;
  total_questions: number;
  accuracy: {
    rag: number;
    graphrag: number;
    agent: number;
  };
  tokens: {
    rag_total: number;
    graphrag_total: number;
    agent_total: number;
    rag_avg: number;
    graphrag_avg: number;
    agent_avg: number;
  };
  latency: {
    rag_wall_clock_s: number;
    graphrag_wall_clock_s: number;
    agent_wall_clock_s: number;
    rag_avg_s: number;
    graphrag_avg_s: number;
    agent_avg_s: number;
  };
  agent_steps: {
    total_steps: number;
    avg_steps: number;
  };
}

export interface BenchmarkDataset {
  summary: BenchmarkSummary;
  type_breakdown: Record<string, QueryTypeStats>;
  questions: BenchmarkQuestion[];
}

export type ViewTab =
  | 'overview'
  | 'explorer'
  | 'comparison'
  | 'query_types'
  | 'agent_traces'
  | 'retrieval'
  | 'methodology';
