import json
from pathlib import Path
from agentic_pipeline.config import SQLITE_DB_PATH, DEFAULT_OLLAMA_MODEL
from agentic_pipeline.graph.sqlite_graph import SQLiteGraph
from agentic_pipeline.tools.suite import ToolSuite
from agentic_pipeline.agent.orchestrator import AgenticOrchestrator
from agentic_pipeline.llm_interface import OllamaLLM, set_active_llm

q = "How many nations competed in Judo at the 2016 Summer Olympics – Women's 57 kg?"

graph = SQLiteGraph(str(SQLITE_DB_PATH))
suite = ToolSuite(graph)
llm = OllamaLLM(model_name=DEFAULT_OLLAMA_MODEL)
set_active_llm(llm)

# Test evaluate_evidence bug directly:
ev = [{"step": 1, "tool": "get_events", "args": {}, "output": [{"title": "test"}]}]
res = suite.evaluate_evidence(q, ev)
print("Testing evaluate_evidence output:")
print(json.dumps(res, indent=2))
