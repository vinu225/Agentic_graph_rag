# Submission Artifacts: Results on 50 Hidden Questions

This directory contains the official raw outputs and benchmark evaluations for the **50 Hidden Questions** as requested by the submission specification.

---

## 📁 Generated Submission Files

| File | Scope | Format | Size | Description |
| :--- | :--- | :--- | :--- | :--- |
| [`submission_50_hidden_tri_pipeline.json`](file:///c:/LATEST/RAG/Agentic_graph_rag/submission_50_hidden_tri_pipeline.json) | **All 3 Pipelines** | JSON (Indented) | 145 KB | Complete outputs for Plain RAG, GraphRAG, and Agentic GraphRAG with token breakdowns, latencies, and agentic traces. |
| [`submission_50_hidden_tri_pipeline.jsonl`](file:///c:/LATEST/RAG/Agentic_graph_rag/submission_50_hidden_tri_pipeline.jsonl) | **All 3 Pipelines** | JSONL (Streaming) | 88.5 KB | Line-delimited JSON objects per question for automated validation platforms. |
| [`submission_50_hidden_agentic_graphrag.json`](file:///c:/LATEST/RAG/Agentic_graph_rag/submission_50_hidden_agentic_graphrag.json) | **Agentic GraphRAG Only** | JSON (Indented) | 88.5 KB | Dedicated standalone submission containing generated answers, token metrics, and complete step-by-step ReAct agent traces. |
| [`submission_50_hidden_agentic_graphrag.jsonl`](file:///c:/LATEST/RAG/Agentic_graph_rag/submission_50_hidden_agentic_graphrag.jsonl) | **Agentic GraphRAG Only** | JSONL (Streaming) | 59.0 KB | Line-delimited raw outputs for Agentic GraphRAG. |

---

## 📊 Summary of Benchmark Execution (50 Hidden Questions)

- **Evaluation Dataset**: 50 Hidden Olympic Evaluation Questions (`eval-001` through `eval-050`)
- **Query Taxonomies**: Aggregation (15), Multi-hop (10), Temporal (8), Superlative (10), Lookup (7)
- **Primary Generator LLM**: `Qwen 2.5 8B Instruct` (Local via Ollama)
- **Graph Backends**: SQLite (`local_graph.db`) / TigerGraph Savanna DB

### Aggregate Performance Across Pipelines

| Dimension | Plain RAG (BM25) | Deterministic GraphRAG | Autonomous Agentic GraphRAG |
| :--- | :--- | :--- | :--- |
| **Total Questions** | 50 | 50 | 50 |
| **Total Tokens Consumed** | 112,272 | 115,240 | 285,814 |
| **Average Tokens / Question** | 2,245 tokens | 2,305 tokens | 5,716 tokens |
| **Average Wall-Clock Latency** | 8.99s | 7.74s | 19.89s |
| **Average Reasoning Hops** | N/A (1-shot) | N/A (1-shot) | **3.58 hops** (179 total hops) |

---

## 🔍 Data Structure of Submission Records

### 1. Tri-Pipeline Record Schema (`submission_50_hidden_tri_pipeline.json`)
```json
{
  "question_id": "eval-001",
  "query_type": "multi_hop",
  "question": "Who won the gold medal in the event held at Olympic Tennis Centre on 15 to 22 August 2004?",
  "pipelines": {
    "plain_rag": {
      "answer": "...",
      "tokens_used": 2706,
      "token_breakdown": { "input_tokens": 2630, "output_tokens": 76, "context_tokens": 1887 },
      "latency_seconds": 21.361,
      "citations": ["Q734997#c0", "Q942805#c0"]
    },
    "graphrag": {
      "answer": "...",
      "tokens_used": 1228,
      "token_breakdown": { "input_tokens": 1209, "output_tokens": 19, "context_tokens": 781 },
      "latency_seconds": 16.261,
      "citations": ["Q942805#c0"]
    },
    "agentic_graphrag": {
      "answer": "...",
      "tokens_used": 4563,
      "token_breakdown": { "prompt_tokens": 4424, "completion_tokens": 139 },
      "latency_seconds": 19.901,
      "total_steps": 3,
      "stopped_reason": "evidence_sufficient_answered",
      "citations": [],
      "agentic_trace": [
        {
          "step": 1,
          "action": "tool_call",
          "tool": "get_events",
          "args": { "venue": "Olympic Tennis Centre", "date": "15 to 22 August 2004", "games": "2004 Summer", "limit": 1 },
          "duration_s": 8.03,
          "tokens": 1270
        },
        {
          "step": 2,
          "action": "tool_call",
          "tool": "get_event_attributes",
          "args": { "event_id_or_title": "Tennis at the 2004 Summer Olympics – Women's doubles" },
          "duration_s": 5.48,
          "tokens": 1426
        },
        {
          "step": 3,
          "action": "final_answer",
          "tool": null,
          "args": null,
          "duration_s": 6.39,
          "tokens": 1867
        }
      ]
    }
  }
}
```

### 2. Standalone Agentic GraphRAG Record Schema (`submission_50_hidden_agentic_graphrag.json`)
```json
{
  "question_id": "eval-001",
  "query_type": "multi_hop",
  "question": "Who won the gold medal in the event held at Olympic Tennis Centre on 15 to 22 August 2004?",
  "system": "Agentic GraphRAG (ReAct Loop + Deterministic Graph Tools)",
  "answer": "The gold medal in the Women's doubles tennis event held at the Olympic Tennis Centre from 15 to 22 August 2004 was won by Li Ting and Sun Tiantian from China.",
  "tokens_used": 4563,
  "token_breakdown": {
    "prompt_tokens": 4424,
    "completion_tokens": 139
  },
  "latency_seconds": 19.901,
  "total_reasoning_steps": 3,
  "stopped_reason": "evidence_sufficient_answered",
  "citations": [],
  "agentic_trace": [ ... ]
}
```
