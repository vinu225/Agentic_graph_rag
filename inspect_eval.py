import json
from pathlib import Path

WORKSPACE_ROOT = Path("c:/LATEST/RAG/Agentic_graph_rag")
eval_path = WORKSPACE_ROOT / "drive-download-20260928T175718Z-1-001/questions/eval_public.jsonl"
rag_path = WORKSPACE_ROOT / "rag_only_pipeline/results_rag.jsonl"
gr_path = WORKSPACE_ROOT / "results_graphrag.jsonl"
ag_path = WORKSPACE_ROOT / "results_agentic.jsonl"

selected = [
    "pub-001", "pub-003", "pub-010",
    "pub-002", "pub-006", "pub-007",
    "pub-004", "pub-008", "pub-021",
    "pub-005", "pub-011", "pub-014",
    "pub-009", "pub-025", "pub-029"
]

q_map = {}
with open(eval_path, encoding='utf-8') as f:
    for line in f:
        if line.strip():
            item = json.loads(line)
            q_map[item['qid']] = item

rag_map = {}
with open(rag_path, encoding='utf-8') as f:
    for line in f:
        if line.strip():
            item = json.loads(line)
            rag_map[item['question_id']] = item

gr_map = {}
if gr_path.exists():
    with open(gr_path, encoding='utf-8') as f:
        for line in f:
            if line.strip():
                item = json.loads(line)
                gr_map[item['question_id']] = item

ag_map = {}
if ag_path.exists():
    with open(ag_path, encoding='utf-8') as f:
        for line in f:
            if line.strip():
                item = json.loads(line)
                ag_map[item['question_id']] = item

print(f"Total Selected: {len(selected)}")
print(f"RAG evaluated: {len(rag_map)} total, {sum(1 for q in selected if q in rag_map)} in selected")
print(f"GraphRAG evaluated: {len(gr_map)} in selected: {[q for q in selected if q in gr_map]}")
print(f"Agentic evaluated: {len(ag_map)} in selected: {[q for q in selected if q in ag_map]}")

for qid in selected:
    q = q_map[qid]
    r = rag_map.get(qid, {})
    g = gr_map.get(qid, {})
    a = ag_map.get(qid, {})
    print("-" * 60)
    print(f"[{qid}] Type: {q['qtype']}")
    print(f"  Q: {q['question']}")
    print(f"  Gold: {q['answer']}")
    print(f"  RAG: {r.get('answer', 'N/A')[:80]}")
    print(f"  GR:  {g.get('answer', 'N/A')[:80]}")
    print(f"  AG:  {a.get('answer', 'N/A')[:80]}")
