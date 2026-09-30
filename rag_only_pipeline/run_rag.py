"""CLI runner for the independent RAG pipeline.
Usage:
    python run_rag.py --question "Who won gold in..."
    python run_rag.py --eval-sample 5 --mock
    python run_rag.py --eval-sample 100 --model qwen3:8b --output results_rag.jsonl
"""

import sys
import json
import argparse
from pathlib import Path

# Ensure utf-8 output on Windows console
if sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add workspace root to path so rag_only_pipeline package resolves correctly
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rag_only_pipeline.config import (
    EVAL_PUBLIC_PATH,
    DEFAULT_K,
    DEFAULT_MODEL,
    DEFAULT_OUTPUT_PATH,
    SQLITE_DB_PATH,
)
from rag_only_pipeline.llm.llm_client import MockLLM, OllamaLLM, set_active_llm
from rag_only_pipeline.pipeline import RAGPipeline
from rag_only_pipeline.retrieval.bm25_index import BM25Index


def run_single(question: str, k: int, pipeline: RAGPipeline, question_id: str = "adhoc") -> None:
    print(f"\nQuestion: {question}")
    print(f"Retrieving top-{k} chunks and generating answer...")
    res = pipeline.run(question=question, question_id=question_id, k=k)
    print(f"\nAnswer:         {res.answer}")
    print(f"Citations:      {res.citations}")
    print(f"Context Tokens: {res.context_tokens}")
    print(f"Input Tokens:   {res.input_tokens}")
    print(f"Output Tokens:  {res.output_tokens}")
    print(f"Total Tokens:   {res.total_tokens}")
    print(f"Elapsed:        {res.elapsed_time_s:.3f}s")
    print(f"\nJSONL Row:")
    print(json.dumps(res.to_dict(), ensure_ascii=False))


def run_eval_sample(
    num_questions: int,
    k: int,
    pipeline: RAGPipeline,
    output_path: Path,
) -> None:
    if not EVAL_PUBLIC_PATH.exists():
        print(f"Error: Evaluation file not found at {EVAL_PUBLIC_PATH}")
        sys.exit(1)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    results_written = 0

    print(f"\n=== RAG Pipeline Evaluation ===")
    print(f"  Source:       {EVAL_PUBLIC_PATH.name}")
    print(f"  Questions:    {num_questions}")
    print(f"  k (top-k):    {k}")
    print(f"  Output file:  {output_path}")
    print("=" * 60)

    with open(EVAL_PUBLIC_PATH, "r", encoding="utf-8") as f_in, \
         open(output_path, "w", encoding="utf-8") as f_out:

        for idx, line in enumerate(f_in):
            if idx >= num_questions:
                break
            line = line.strip()
            if not line:
                continue

            item = json.loads(line)
            qid = item["qid"]
            question_text = item["question"]
            qtype = item.get("qtype", "unknown")
            gold_answer = item.get("answer", [])

            try:
                res = pipeline.run(question=question_text, question_id=qid, k=k)
                row = res.to_dict()

                f_out.write(json.dumps(row, ensure_ascii=False) + "\n")
                results_written += 1

                print(f"[{qid}] ({qtype}) {question_text}")
                print(f"  Gold:     {gold_answer}")
                print(f"  Answer:   {res.answer}")
                print(f"  Citations:{res.citations}")
                print(f"  Tokens:   ctx={res.context_tokens} | in={res.input_tokens} | out={res.output_tokens} | total={res.total_tokens}")
                print(f"  Elapsed:  {res.elapsed_time_s:.3f}s")
                print()

            except Exception as e:
                print(f"  [ERROR] {qid}: {e}")

    print(f"=== Done. Wrote {results_written} results to {output_path} ===")


def main() -> None:
    parser = argparse.ArgumentParser(description="RAG Pipeline CLI Runner")
    parser.add_argument("--question", type=str, default=None,
                        help="A single question to run RAG on")
    parser.add_argument("--qid", type=str, default=None,
                        help="Run a specific question ID from eval_public.jsonl (e.g. pub-004)")
    parser.add_argument("--eval-sample", type=int, default=0, metavar="N",
                        help="Run first N questions from eval_public.jsonl")
    parser.add_argument("--k", type=int, default=DEFAULT_K,
                        help=f"Number of chunks to retrieve (default: {DEFAULT_K})")
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL,
                        help=f"Ollama model name (default: {DEFAULT_MODEL})")
    parser.add_argument("--mock", action="store_true",
                        help="Use MockLLM (offline mode, no Ollama required)")
    parser.add_argument("--output", type=str, default=str(DEFAULT_OUTPUT_PATH),
                        help=f"Output JSONL path (default: {DEFAULT_OUTPUT_PATH})")

    args = parser.parse_args()

    # Select LLM backend
    if args.mock:
        print("[Mode] MockLLM (offline)")
        set_active_llm(MockLLM())
    else:
        print(f"[Mode] OllamaLLM | model={args.model}")
        set_active_llm(OllamaLLM(model_name=args.model))

    # Initialize index and pipeline
    index = BM25Index(db_path=SQLITE_DB_PATH)
    if not index.is_indexed():
        print("[Info] BM25 index not found. Building from corpus...")
        index.build_index(verbose=True)
    else:
        with index._get_connection() as conn:
            count = conn.execute("SELECT count(*) FROM chunks").fetchone()[0]
        print(f"[Info] BM25 index ready ({count} chunks).")

    pipeline = RAGPipeline(index=index)
    output_path = Path(args.output)

    if args.qid:
        with open(EVAL_PUBLIC_PATH, "r", encoding="utf-8") as f_in:
            target = next((json.loads(l) for l in f_in if json.loads(l).get("qid") == args.qid), None)
        if not target:
            print(f"[Error] Question ID '{args.qid}' not found in {EVAL_PUBLIC_PATH}")
            sys.exit(1)
        print(f"\n[{target['qid']}] ({target.get('qtype', 'unknown')}) {target['question']}")
        print(f"  Gold: {target.get('answer', [])}")
        run_single(question=target["question"], k=args.k, pipeline=pipeline, question_id=target["qid"])
    elif args.eval_sample > 0:
        run_eval_sample(
            num_questions=args.eval_sample,
            k=args.k,
            pipeline=pipeline,
            output_path=output_path,
        )
    elif args.question:
        run_single(question=args.question, k=args.k, pipeline=pipeline)
    else:
        # Default: single sample question
        sample = "According to the provided corpus, how many shooting events at the 2004 Summer Olympics had more than 37 competitors?"
        run_single(question=sample, k=args.k, pipeline=pipeline)


if __name__ == "__main__":
    main()
