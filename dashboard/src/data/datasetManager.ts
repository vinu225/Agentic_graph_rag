import rawBenchmarks from './benchmarks.json';
import { BenchmarkDataset, BenchmarkQuestion, QueryTypeStats } from '../types/benchmark';

// Normalize 15q dataset to match BenchmarkDataset interface
function normalize15q(raw: any): BenchmarkDataset {
  const summaryRaw = raw.summary || {};
  const byTypeRaw = summaryRaw.by_type || {};

  const type_breakdown: Record<string, QueryTypeStats> = {};
  for (const [key, val] of Object.entries<any>(byTypeRaw)) {
    type_breakdown[key] = {
      total: val.total || 0,
      accuracy: {
        rag: val.accuracy?.RAG ?? val.accuracy?.rag ?? 0,
        graphrag: val.accuracy?.GraphRAG ?? val.accuracy?.graphrag ?? 0,
        agent: val.accuracy?.Agent ?? val.accuracy?.agent ?? 0,
      },
      tokens_avg: {
        rag: val.tokens?.RAG ?? val.tokens?.rag ?? 0,
        graphrag: val.tokens?.GraphRAG ?? val.tokens?.graphrag ?? 0,
        agent: val.tokens?.Agent ?? val.tokens?.agent ?? 0,
      },
      latency_avg_s: {
        rag: val.latency_s?.RAG ?? val.latency_s?.rag ?? 0,
        graphrag: val.latency_s?.GraphRAG ?? val.latency_s?.graphrag ?? 0,
        agent: val.latency_s?.Agent ?? val.latency_s?.agent ?? 0,
      },
      agent_avg_steps: val.agent_avg_steps || 3.0,
    };
  }

  const questions: BenchmarkQuestion[] = (raw.questions || []).map((q: any) => ({
    question_id: q.question_id,
    query_type: q.query_type,
    question: q.question,
    gold_answer: q.gold_answer,
    rag: {
      answer: q.rag?.answer || '',
      correct: q.rag?.correct ?? false,
      tokens: q.rag?.tokens ?? 0,
      elapsed_time_s: q.rag?.elapsed_time_s ?? q.rag?.latency ?? 0,
      latency: q.rag?.latency ?? q.rag?.elapsed_time_s ?? 0,
      citations: q.rag?.citations || [],
    },
    graphrag: {
      answer: q.graphrag?.answer || '',
      correct: q.graphrag?.correct ?? false,
      tokens: q.graphrag?.tokens ?? 0,
      elapsed_time_s: q.graphrag?.elapsed_time_s ?? q.graphrag?.latency ?? 0,
      latency: q.graphrag?.latency ?? q.graphrag?.elapsed_time_s ?? 0,
      citations: q.graphrag?.citations || [],
    },
    agent: {
      answer: q.agent?.answer || '',
      correct: q.agent?.correct ?? false,
      tokens: q.agent?.tokens ?? 0,
      elapsed_time_s: q.agent?.elapsed_time_s ?? q.agent?.latency ?? 0,
      latency: q.agent?.latency ?? q.agent?.elapsed_time_s ?? 0,
      total_steps: q.agent?.total_steps ?? 3,
      stopped_reason: q.agent?.stopped_reason,
      trace: q.agent?.trace || [],
      citations: q.agent?.citations || [],
    },
  }));

  return {
    summary: {
      benchmark_scale: "15-Question Presentation Subset",
      timestamp: summaryRaw.timestamp || "2026-10-04 (Initial Calibration)",
      total_questions: 15,
      accuracy: {
        rag: summaryRaw.overall_accuracy?.RAG ?? 66.7,
        graphrag: summaryRaw.overall_accuracy?.GraphRAG ?? 93.3,
        agent: summaryRaw.overall_accuracy?.Agent ?? 100.0,
      },
      tokens: {
        rag_total: Math.round((summaryRaw.average_tokens?.RAG || 2160) * 15),
        graphrag_total: Math.round((summaryRaw.average_tokens?.GraphRAG || 2172) * 15),
        agent_total: Math.round((summaryRaw.average_tokens?.Agent || 4780) * 15),
        rag_avg: Math.round(summaryRaw.average_tokens?.RAG || 2160),
        graphrag_avg: Math.round(summaryRaw.average_tokens?.GraphRAG || 2172),
        agent_avg: Math.round(summaryRaw.average_tokens?.Agent || 4780),
      },
      latency: {
        rag_wall_clock_s: (summaryRaw.average_latency_s?.RAG || 10.9) * 15,
        graphrag_wall_clock_s: (summaryRaw.average_latency_s?.GraphRAG || 15.3) * 15,
        agent_wall_clock_s: (summaryRaw.average_latency_s?.Agent || 17.8) * 15,
        rag_avg_s: summaryRaw.average_latency_s?.RAG || 10.97,
        graphrag_avg_s: summaryRaw.average_latency_s?.GraphRAG || 15.33,
        agent_avg_s: summaryRaw.average_latency_s?.Agent || 17.87,
      },
      agent_steps: {
        total_steps: Math.round((summaryRaw.agent_average_steps || 3.0) * 15),
        avg_steps: summaryRaw.agent_average_steps || 3.0,
      },
    },
    type_breakdown,
    questions,
  };
}

export const benchmarkDatasets: Record<string, BenchmarkDataset> = {
  '100_final': rawBenchmarks.benchmark_100 as unknown as BenchmarkDataset,
  '15_presentation': normalize15q(rawBenchmarks.benchmark_15),
};

export const benchmarkKeys = [
  { id: '100_final', name: '100-Question Public Benchmark (Final Optimized)', count: 100, timestamp: '2026-10-05 16:26', default: true },
  { id: '15_presentation', name: '15-Question Presentation Subset (Baseline)', count: 15, timestamp: '2026-10-04 Calibration', default: false }
];
