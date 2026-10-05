"""Diagnostic script to capture full raw execution traces for pub-008 and pub-025,
and profile GraphRAG latency on pub-008 and pub-014.
Strict adherence to integrity constraint: no gold answers read or evaluated.
"""

import sys
import json
import time
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

WORKSPACE_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(WORKSPACE_ROOT))

from agentic_pipeline.config import SQLITE_DB_PATH, DEFAULT_OLLAMA_MODEL
from agentic_pipeline.graph.sqlite_graph import SQLiteGraph
from agentic_pipeline.tools.suite import ToolSuite
from agentic_pipeline.agent.orchestrator import AgenticOrchestrator
from agentic_pipeline.llm_interface import OllamaLLM, set_active_llm
from graphrag_pipeline.pipeline import GraphRAGPipeline

Q_PUB_008 = "According to the provided corpus, which sailing event at the 2000 Summer Olympics had the highest number of competitors?"
Q_PUB_025 = "How many nations competed in Judo at the 2016 Summer Olympics – Women's 57 kg?"
Q_PUB_014 = "Who won the gold medal in the event held at Riocentro – Pavilion 4 on 11–19 August at the 2016 Summer Olympics?"

def print_trace(result):
    print(f"\nTotal Steps: {result.total_steps}")
    print(f"Total Tokens: {result.total_tokens} (prompt: {result.prompt_tokens}, completion: {result.completion_tokens})")
    print(f"Elapsed Time: {result.elapsed_time_s:.2f}s")
    print(f"Stopped Reason: {result.stopped_reason}")
    print(f"Final Answer: {result.answer}")
    print("\n--- DETAILED STEP-BY-STEP TRACE ---")
    for step in result.trace:
        print(f"\n[Step {step.step_num}] Action: {step.action_type} | Duration: {step.duration_s:.2f}s | Tokens: {step.tokens}")
        if step.action_type == "tool_call":
            print(f"  Tool: {step.tool_name}")
            print(f"  Arguments: {json.dumps(step.tool_input, indent=2)}")
            out_str = json.dumps(step.tool_output, indent=2, default=str)
            if len(out_str) > 600:
                print(f"  Output (truncated, total {len(out_str)} chars):\n{out_str[:600]}...")
            else:
                print(f"  Output:\n{out_str}")
        elif step.action_type == "final_answer":
            print(f"  Thought/Answer:\n{step.thought}")

def diagnose():
    print("=" * 80)
    print("DIAGNOSIS 1: Agent Execution Trace on pub-008")
    print(f"Question: {Q_PUB_008}")
    print("=" * 80)

    shared_llm = OllamaLLM(model_name=DEFAULT_OLLAMA_MODEL)
    set_active_llm(shared_llm)

    graph = SQLiteGraph(str(SQLITE_DB_PATH))
    tool_suite = ToolSuite(graph)
    orchestrator = AgenticOrchestrator(tool_suite)

    res_008 = orchestrator.run(Q_PUB_008)
    print_trace(res_008)

    print("\n" + "=" * 80)
    print("DIAGNOSIS 2: Agent Execution Trace on pub-025")
    print(f"Question: {Q_PUB_025}")
    print("=" * 80)

    res_025 = orchestrator.run(Q_PUB_025)
    print_trace(res_025)

    graph.close()

    print("\n" + "=" * 80)
    print("DIAGNOSIS 3: GraphRAG Latency Profiling on pub-008 and pub-014")
    print("=" * 80)

    graphrag_pipe = GraphRAGPipeline(model_name=DEFAULT_OLLAMA_MODEL, llm=shared_llm)
    
    # Profile pub-008
    t0 = time.time()
    f_008 = graphrag_pipe.extract_filters(Q_PUB_008)
    t_filt = time.time() - t0
    
    t1 = time.time()
    ev_008 = graphrag_pipe.graph.get_events(
        games=f_008.get("games"),
        sport=f_008.get("sport"),
        limit=50
    )
    t_ev = time.time() - t1

    t2 = time.time()
    chunks_008 = graphrag_pipe.bm25.search(Q_PUB_008, top_k=2)
    t_bm25 = time.time() - t2

    print(f"\n[pub-008 GraphRAG Breakdown]")
    print(f"  Filters: {f_008} ({t_filt*1000:.1f}ms)")
    print(f"  Events retrieved: {len(ev_008)} ({t_ev*1000:.1f}ms)")
    for e in ev_008[:5]:
        print(f"    - [{e['doc_id']}] {e['title']} | comp: {e.get('competitors')}")
    print(f"  BM25 search: {len(chunks_008)} chunks ({t_bm25*1000:.1f}ms)")

    t3 = time.time()
    gr_res_008 = graphrag_pipe.run(Q_PUB_008)
    t_total_008 = time.time() - t3
    print(f"  End-to-End GraphRAG run: {t_total_008:.2f}s | Tokens: {gr_res_008.total_tokens}")
    print(f"  GraphRAG answer: {gr_res_008.answer}")

    # Profile pub-014
    print(f"\n[pub-014 GraphRAG Breakdown]")
    t0 = time.time()
    f_014 = graphrag_pipe.extract_filters(Q_PUB_014)
    t_filt = time.time() - t0
    
    t1 = time.time()
    ev_014 = graphrag_pipe.graph.get_events(
        games=f_014.get("games"),
        sport=f_014.get("sport"),
        venue=f_014.get("venue"),
        date=f_014.get("date"),
        limit=50
    )
    t_ev = time.time() - t1

    t2 = time.time()
    chunks_014 = graphrag_pipe.bm25.search(Q_PUB_014, top_k=2)
    t_bm25 = time.time() - t2

    print(f"  Filters: {f_014} ({t_filt*1000:.1f}ms)")
    print(f"  Events retrieved: {len(ev_014)} ({t_ev*1000:.1f}ms)")
    for e in ev_014:
        print(f"    - [{e['doc_id']}] {e['title']}")
    print(f"  BM25 search: {len(chunks_014)} chunks ({t_bm25*1000:.1f}ms)")

    t3 = time.time()
    gr_res_014 = graphrag_pipe.run(Q_PUB_014)
    t_total_014 = time.time() - t3
    print(f"  End-to-End GraphRAG run: {t_total_014:.2f}s | Tokens: {gr_res_014.total_tokens}")
    print(f"  GraphRAG answer: {gr_res_014.answer}")

    graphrag_pipe.close()

if __name__ == "__main__":
    diagnose()
