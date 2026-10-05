import sys
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

# Test pub-010
q010 = "According to the provided corpus, how many cycling events at the 2000 Summer Olympics had more than 30 competitors?"
res010 = orchestrator.run(q010)
print("=== PUB-010 ===")
print("Answer:", res010.answer)
print("Steps:", res010.total_steps, "Tokens:", res010.total_tokens)
for s in res010.trace:
    print(f"  Step {s.step_num} ({s.action_type}): {s.tool_name} {s.tool_input}")

# Test pub-006
q006 = "Who won the gold medal in the women's 57 kg judo event at the Summer Olympics held immediately before 2020?"
res006 = orchestrator.run(q006)
print("\n=== PUB-006 ===")
print("Answer:", res006.answer)
print("Steps:", res006.total_steps, "Tokens:", res006.total_tokens)
for s in res006.trace:
    print(f"  Step {s.step_num} ({s.action_type}): {s.tool_name} {s.tool_input}")

graph.close()
