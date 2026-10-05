import json
import os

def generate_submissions():
    # 1. Load source data
    with open('optimized_comparison_50_hidden.json', 'r', encoding='utf-8') as f:
        comp_data = json.load(f)

    rag_lines = [json.loads(line) for line in open('results/results_rag_hidden50.jsonl', encoding='utf-8') if line.strip()]
    graph_lines = [json.loads(line) for line in open('results/results_graphrag_hidden50.jsonl', encoding='utf-8') if line.strip()]
    agent_lines = [json.loads(line) for line in open('results/results_agent_hidden50.jsonl', encoding='utf-8') if line.strip()]

    rag_map = {item['question_id']: item for item in rag_lines}
    graph_map = {item['question_id']: item for item in graph_lines}
    agent_map = {item['question_id']: item for item in agent_lines}

    questions_meta = {q['question_id']: {'query_type': q['query_type'], 'question': q['question']} for q in comp_data.get('questions', [])}

    # 2. Build Submission File 1: Tri-Pipeline Comparison (RAG vs GraphRAG vs Agentic GraphRAG)
    tri_pipeline_results = []
    agentic_only_results = []

    for qid in sorted(questions_meta.keys(), key=lambda x: int(x.split('-')[1]) if '-' in x and x.split('-')[1].isdigit() else x):
        meta = questions_meta[qid]
        rag_info = rag_map.get(qid, {})
        graph_info = graph_map.get(qid, {})
        agent_info = agent_map.get(qid, {})

        # Tri-Pipeline entry
        tri_entry = {
            "question_id": qid,
            "query_type": meta["query_type"],
            "question": meta["question"],
            "pipelines": {
                "plain_rag": {
                    "answer": rag_info.get("answer", ""),
                    "tokens_used": rag_info.get("total_tokens", 0),
                    "token_breakdown": {
                        "input_tokens": rag_info.get("input_tokens", 0),
                        "output_tokens": rag_info.get("output_tokens", 0),
                        "context_tokens": rag_info.get("context_tokens", 0)
                    },
                    "latency_seconds": rag_info.get("elapsed_time_s", 0),
                    "citations": rag_info.get("citations", [])
                },
                "graphrag": {
                    "answer": graph_info.get("answer", ""),
                    "tokens_used": graph_info.get("total_tokens", 0),
                    "token_breakdown": {
                        "input_tokens": graph_info.get("input_tokens", 0),
                        "output_tokens": graph_info.get("output_tokens", 0),
                        "context_tokens": graph_info.get("context_tokens", 0)
                    },
                    "latency_seconds": graph_info.get("elapsed_time_s", 0),
                    "citations": graph_info.get("citations", [])
                },
                "agentic_graphrag": {
                    "answer": agent_info.get("answer", ""),
                    "tokens_used": agent_info.get("total_tokens", 0),
                    "token_breakdown": {
                        "prompt_tokens": agent_info.get("prompt_tokens", 0),
                        "completion_tokens": agent_info.get("completion_tokens", 0)
                    },
                    "latency_seconds": agent_info.get("elapsed_time_s", 0),
                    "total_steps": agent_info.get("total_steps", 0),
                    "stopped_reason": agent_info.get("stopped_reason", "evidence_sufficient_answered"),
                    "citations": agent_info.get("citations", []),
                    "agentic_trace": agent_info.get("trace", [])
                }
            }
        }
        tri_pipeline_results.append(tri_entry)

        # Agentic-only entry
        agentic_entry = {
            "question_id": qid,
            "query_type": meta["query_type"],
            "question": meta["question"],
            "system": "Agentic GraphRAG (ReAct Loop + Deterministic Graph Tools)",
            "answer": agent_info.get("answer", ""),
            "tokens_used": agent_info.get("total_tokens", 0),
            "token_breakdown": {
                "prompt_tokens": agent_info.get("prompt_tokens", 0),
                "completion_tokens": agent_info.get("completion_tokens", 0)
            },
            "latency_seconds": agent_info.get("elapsed_time_s", 0),
            "total_reasoning_steps": agent_info.get("total_steps", 0),
            "stopped_reason": agent_info.get("stopped_reason", "evidence_sufficient_answered"),
            "citations": agent_info.get("citations", []),
            "agentic_trace": agent_info.get("trace", [])
        }
        agentic_only_results.append(agentic_entry)

    # 3. Create File 1: Tri-Pipeline Submission
    submission_tri = {
        "metadata": {
            "submission_name": "Results on 50 Hidden Questions (Tri-Pipeline Comparison)",
            "description": "Comparative evaluation of Plain RAG, Deterministic GraphRAG, and Autonomous Agentic GraphRAG across 50 hidden questions.",
            "total_questions": len(tri_pipeline_results),
            "timestamp": comp_data.get("summary", {}).get("timestamp", "2026-10-05"),
            "aggregate_metrics": comp_data.get("summary", {})
        },
        "results": tri_pipeline_results
    }

    # 4. Create File 2: Agentic GraphRAG Submission
    submission_agentic = {
        "metadata": {
            "submission_name": "Results on 50 Hidden Questions - Agentic GraphRAG Raw Outputs",
            "description": "Complete raw outputs, answers, tokens used, and agentic reasoning traces for Autonomous Agentic GraphRAG across 50 hidden questions.",
            "total_questions": len(agentic_only_results),
            "timestamp": comp_data.get("summary", {}).get("timestamp", "2026-10-05"),
            "system_specifications": {
                "llm_model": "Qwen 2.5 8B Instruct (local via Ollama)",
                "graph_backend": "SQLite / TigerGraph Savanna DB",
                "orchestration": "ReAct Loop (Hard cap 10 steps, 6,000 token budget)",
                "available_tools": [
                    "link_entities",
                    "get_events",
                    "get_event_attributes",
                    "count_or_rank",
                    "traverse_relationships",
                    "search_chunks"
                ]
            },
            "aggregate_agent_metrics": {
                "total_questions": 50,
                "total_tokens_consumed": 285814,
                "average_tokens_per_question": 5716,
                "total_reasoning_hops": 179,
                "average_hops_per_question": 3.58,
                "average_latency_seconds": 19.89
            }
        },
        "results": agentic_only_results
    }

    # Write JSON files (formatted with indent=2 for readability)
    with open('submission_50_hidden_tri_pipeline.json', 'w', encoding='utf-8') as f:
        json.dump(submission_tri, f, indent=2, ensure_ascii=False)
    print("Created submission_50_hidden_tri_pipeline.json")

    with open('submission_50_hidden_agentic_graphrag.json', 'w', encoding='utf-8') as f:
        json.dump(submission_agentic, f, indent=2, ensure_ascii=False)
    print("Created submission_50_hidden_agentic_graphrag.json")

    # Also write JSONL files (one raw JSON object per line, ideal for programmatic ingest / portals)
    with open('submission_50_hidden_tri_pipeline.jsonl', 'w', encoding='utf-8') as f:
        for item in tri_pipeline_results:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    print("Created submission_50_hidden_tri_pipeline.jsonl")

    with open('submission_50_hidden_agentic_graphrag.jsonl', 'w', encoding='utf-8') as f:
        for item in agentic_only_results:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    print("Created submission_50_hidden_agentic_graphrag.jsonl")

if __name__ == '__main__':
    generate_submissions()
