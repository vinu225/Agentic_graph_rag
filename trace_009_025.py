import sys
import json
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

WORKSPACE_ROOT = Path("c:/LATEST/RAG/Agentic_graph_rag")
sys.path.insert(0, str(WORKSPACE_ROOT))

from agentic_pipeline.config import SQLITE_DB_PATH, DEFAULT_OLLAMA_MODEL
from agentic_pipeline.graph.sqlite_graph import SQLiteGraph
from agentic_pipeline.tools.suite import ToolSuite
from agentic_pipeline.agent.orchestrator import AgenticOrchestrator
from agentic_pipeline.llm_interface import OllamaLLM, set_active_llm

graph = SQLiteGraph(str(SQLITE_DB_PATH))
suite = ToolSuite(graph)
llm = OllamaLLM(model_name=DEFAULT_OLLAMA_MODEL)
set_active_llm(llm)
orchestrator = AgenticOrchestrator(suite)

q009 = "How many nations competed in Sailing at the 2016 Summer Olympics – Women's RS:X?"
print(f"Running pub-009: {q009}")
res009 = orchestrator.run(q009)
print(f"pub-009 result: steps={res009.total_steps}, stopped={res009.stopped_reason}, tokens={res009.total_tokens}")
for step in res009.trace:
    print(f"  Step {step.step_num}: {step.action_type} - {step.tool_name} {step.tool_input}")

q025 = "How many nations competed in Judo at the 2016 Summer Olympics – Women's 57 kg?"
print(f"\nRunning pub-025: {q025}")
res025 = orchestrator.run(q025)
print(f"pub-025 result: steps={res025.total_steps}, stopped={res025.stopped_reason}, tokens={res025.total_tokens}")
for step in res025.trace:
    print(f"  Step {step.step_num}: {step.action_type} - {step.tool_name} {step.tool_input}")
    if step.action_type == "tool_call":
        out_str = str(step.tool_output)
        if len(out_str) > 200:
            out_str = out_str[:200] + "..."
        print(f"    Output: {out_str}")
print(f"pub-025 answer: {res025.answer}")

graph.close()
