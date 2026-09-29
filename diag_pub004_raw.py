"""Diagnostic script: shows raw unparsed model output for pub-004.
Calls Ollama directly, dumps the full response including any <think> blocks.
Run: python diag_pub004_raw.py
"""
import sys
import json
import urllib.request
from pathlib import Path

if sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.insert(0, str(Path(__file__).resolve().parent))

from rag_only_pipeline.config import EVAL_PUBLIC_PATH, OLLAMA_API_BASE, DEFAULT_MODEL, SQLITE_DB_PATH
from rag_only_pipeline.retrieval.bm25_index import BM25Index
from rag_only_pipeline.prompt import build_rag_prompt

# Load pub-004
item = None
with open(EVAL_PUBLIC_PATH, "r", encoding="utf-8") as f:
    for line in f:
        row = json.loads(line)
        if row["qid"] == "pub-004":
            item = row
            break

print(f"Question: {item['question']}")
print(f"Gold:     {item['answer']}")
print()

# Retrieve chunks
index = BM25Index(db_path=SQLITE_DB_PATH)
chunks = index.search(item["question"], top_k=8)
print(f"Retrieved {len(chunks)} chunks:")
for c in chunks:
    print(f"  [{c['chunk_id']}] {c['title'][:70]}")
print()

# Build prompt
messages = build_rag_prompt(item["question"], chunks)
print(f"Prompt messages count: {len(messages)}")
print(f"Approx prompt chars:   {sum(len(m['content']) for m in messages)}")
print()

# Call Ollama raw - NO parsing, dump everything
payload = {
    "model": DEFAULT_MODEL,
    "messages": messages,
    "temperature": 0.0,
    "max_tokens": 1024,
    "stream": False
}

print(f"Calling {OLLAMA_API_BASE}/chat/completions (model={DEFAULT_MODEL})...")
req = urllib.request.Request(
    f"{OLLAMA_API_BASE}/chat/completions",
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json"}
)

try:
    with urllib.request.urlopen(req, timeout=180) as resp:
        raw_bytes = resp.read()
    res_data = json.loads(raw_bytes.decode("utf-8"))

    print("\n=== RAW RESPONSE (usage) ===")
    print(json.dumps(res_data.get("usage", {}), indent=2))

    choice = res_data.get("choices", [{}])[0]
    raw_content = choice.get("message", {}).get("content", "")
    finish_reason = choice.get("finish_reason", "unknown")

    print(f"\n=== FINISH REASON: {finish_reason} ===")
    print(f"\n=== RAW CONTENT ({len(raw_content)} chars) ===")
    print(repr(raw_content[:500]))
    print("...")
    print(repr(raw_content[-200:]) if len(raw_content) > 500 else "")

    # Check for thinking leak
    if "<think>" in raw_content:
        think_start = raw_content.index("<think>")
        think_end = raw_content.index("</think>") + len("</think>") if "</think>" in raw_content else len(raw_content)
        think_block = raw_content[think_start:think_end]
        after_think = raw_content[think_end:].strip()
        print(f"\n=== THINKING BLOCK DETECTED ({len(think_block)} chars) ===")
        print(f"  First 300 chars of <think>: {repr(think_block[:300])}")
        print(f"\n=== CONTENT AFTER </think> ({len(after_think)} chars) ===")
        print(repr(after_think[:500]))
    else:
        print("\n[No <think> block found in response]")

except Exception as e:
    print(f"Error: {e}")
    print("Ensure Ollama is running (`ollama serve`) and qwen3:8b is pulled.")
