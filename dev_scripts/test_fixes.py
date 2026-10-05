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

# Test 1: pub-008
q008 = "According to the provided corpus, which sailing event at the 2000 Summer Olympics had the highest number of competitors?"
res008 = orchestrator.run(q008)
print("--- PUB-008 ---")
print("Answer:", res008.answer)
print("Steps:", res008.total_steps, "Tokens:", res008.total_tokens)

# Test 2: pub-025
q025 = "How many nations competed in Judo at the 2016 Summer Olympics – Women's 57 kg?"
res025 = orchestrator.run(q025)
print("\n--- PUB-025 ---")
print("Answer:", res025.answer)
print("Steps:", res025.total_steps, "Tokens:", res025.total_tokens)

graph.close()
