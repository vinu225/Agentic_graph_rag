"""Unit tests for the independent RAG pipeline.
Tests:
1. Chunker: infobox detection, chunk field structure, overlap, token bounds
2. BM25Index: indexing, search, top-k results
3. Prompt: message structure, context formatting
4. MockLLM: response structure, citation extraction
5. Pipeline: end-to-end with MockLLM, output schema validation
"""

import json
import sys
import tempfile
from pathlib import Path
from typing import Dict, Any, List

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from rag_only_pipeline.corpus.chunker import chunk_document, estimate_tokens
from rag_only_pipeline.retrieval.bm25_index import BM25Index, sanitize_query_for_fts
from rag_only_pipeline.prompt import build_rag_prompt, format_context_chunks
from rag_only_pipeline.llm.llm_client import (
    MockLLM, LLMResponse, set_active_llm
)
from rag_only_pipeline.pipeline import RAGPipeline, extract_citations, RAGResult


# ─── Sample document matching real corpus structure ───────────────────────────

SAMPLE_DOC_TEXT = """[Infobox Olympic event]
  event: Women's 10 km
  games: 2004 Summer
  venue: Olympic Shooting Centre
  date: 14 August 2004
  competitors: 34
  nations: 22
  gold: Lyubov Galkina
  goldNOC: RUS
  silver: Valentina Turisini
  silverNOC: ITA
  bronze: Zhu Qinan
  bronzeNOC: CHN
  prev: 2000
  next: 2008

The women's 10 m air pistol event at the 2004 Summer Olympics in Athens took place on 14 August 2004.

Competition format
The competition comprised a qualification round and a final round.

Results

Results table
Rank | Athlete | NOC | Score
1 | Lyubov Galkina | RUS | 483.3
2 | Valentina Turisini | ITA | 479.7
3 | Zhu Qinan | CHN | 478.0
"""

SAMPLE_DOC_ID = "QDOC_TEST"
SAMPLE_TITLE = "Shooting at the 2004 Summer Olympics – Women's 10 m air pistol"


# ─── 1. Chunker Tests ─────────────────────────────────────────────────────────

class TestChunker:
    def test_produces_infobox_chunk(self):
        chunks = chunk_document(SAMPLE_DOC_ID, SAMPLE_TITLE, SAMPLE_DOC_TEXT)
        types = [c["chunk_type"] for c in chunks]
        assert "infobox" in types, "Expected at least one infobox chunk"

    def test_infobox_is_first_chunk(self):
        chunks = chunk_document(SAMPLE_DOC_ID, SAMPLE_TITLE, SAMPLE_DOC_TEXT)
        assert chunks[0]["chunk_type"] == "infobox"
        assert chunks[0]["chunk_id"] == f"{SAMPLE_DOC_ID}#c0"

    def test_infobox_contains_gold_field(self):
        chunks = chunk_document(SAMPLE_DOC_ID, SAMPLE_TITLE, SAMPLE_DOC_TEXT)
        infobox = chunks[0]["content"]
        assert "gold:" in infobox or "Lyubov Galkina" in infobox

    def test_all_chunks_have_required_fields(self):
        chunks = chunk_document(SAMPLE_DOC_ID, SAMPLE_TITLE, SAMPLE_DOC_TEXT)
        for c in chunks:
            assert "chunk_id" in c
            assert "doc_id" in c
            assert "title" in c
            assert "chunk_type" in c
            assert "content" in c
            assert c["doc_id"] == SAMPLE_DOC_ID
            assert c["title"] == SAMPLE_TITLE

    def test_chunk_ids_are_unique(self):
        chunks = chunk_document(SAMPLE_DOC_ID, SAMPLE_TITLE, SAMPLE_DOC_TEXT)
        ids = [c["chunk_id"] for c in chunks]
        assert len(ids) == len(set(ids)), "Chunk IDs must be unique"

    def test_chunk_ids_have_correct_prefix(self):
        chunks = chunk_document(SAMPLE_DOC_ID, SAMPLE_TITLE, SAMPLE_DOC_TEXT)
        for c in chunks:
            assert c["chunk_id"].startswith(f"{SAMPLE_DOC_ID}#c")

    def test_empty_text_returns_empty_chunks(self):
        chunks = chunk_document("EMPTY", "Empty Doc", "")
        assert chunks == []

    def test_title_prepended_to_content(self):
        chunks = chunk_document(SAMPLE_DOC_ID, SAMPLE_TITLE, SAMPLE_DOC_TEXT)
        for c in chunks:
            assert c["content"].startswith(f"Title: {SAMPLE_TITLE}")

    def test_estimate_tokens_positive(self):
        assert estimate_tokens("hello world test") > 0

    def test_estimate_tokens_approximate(self):
        text = "A" * 400
        assert 80 <= estimate_tokens(text) <= 120


# ─── 2. BM25 Index Tests ─────────────────────────────────────────────────────

class TestBM25Index:
    @pytest.fixture
    def temp_index(self, tmp_path):
        db_path = tmp_path / "test_rag.db"
        idx = BM25Index(db_path=db_path)
        # Populate with 3 synthetic documents
        docs = [
            {
                "doc_id": "Q_SHOOT_2004",
                "title": "Shooting at the 2004 Summer Olympics",
                "text": SAMPLE_DOC_TEXT
            },
            {
                "doc_id": "Q_CANOE_2012",
                "title": "Canoeing at the 2012 Summer Olympics – Men's K-2 1000 metres",
                "text": "[Infobox Olympic event]\n  event: Men's canoe sprint K-2 1000 metres\n  games: 2012 Summer\n  venue: Eton Dorney\n  gold: Rudolf DombiRoland Kokeny\n  goldNOC: HUN\n  competitors: 24\n  nations: 12\n\nThe men's canoe sprint K-2 1,000 metres took place at Eton Dorney at the 2012 Summer Olympics."
            },
            {
                "doc_id": "Q_SAILING_2016",
                "title": "Sailing at the 2016 Summer Olympics – Women's RS:X",
                "text": "[Infobox Olympic event]\n  event: Women's RS:X\n  games: 2016 Summer\n  venue: Marina da Gloria\n  gold: Marina Alabau\n  goldNOC: ESP\n  nations: 26\n  competitors: 26\n\nThe women's RS:X sailing event took place at Marina da Gloria in 2016."
            }
        ]

        # Build index manually without calling build_index (no corpus file needed)
        import sqlite3
        from rag_only_pipeline.corpus.chunker import chunk_document
        chunk_records = []
        fts_records = []
        for doc in docs:
            chunks = chunk_document(doc["doc_id"], doc["title"], doc["text"])
            for c in chunks:
                chunk_records.append((c["chunk_id"], c["doc_id"], c["title"], c["chunk_type"], c["content"]))
                fts_records.append((c["chunk_id"], c["doc_id"], c["title"], c["content"]))

        with sqlite3.connect(str(db_path)) as conn:
            conn.executemany("INSERT INTO chunks VALUES (?,?,?,?,?)", chunk_records)
            conn.executemany("INSERT INTO chunks_fts VALUES (?,?,?,?)", fts_records)
            conn.commit()

        return idx

    def test_search_returns_list(self, temp_index):
        results = temp_index.search("shooting 2004 Summer Olympics", top_k=3)
        assert isinstance(results, list)

    def test_search_returns_correct_fields(self, temp_index):
        results = temp_index.search("shooting 2004", top_k=2)
        if results:
            for r in results:
                assert "chunk_id" in r
                assert "doc_id" in r
                assert "title" in r
                assert "content" in r
                assert "score" in r

    def test_search_top_k_limit_respected(self, temp_index):
        results = temp_index.search("Olympics", top_k=2)
        assert len(results) <= 2

    def test_search_returns_relevant_doc(self, temp_index):
        results = temp_index.search("shooting 2004 Summer Olympics", top_k=3)
        doc_ids = [r["doc_id"] for r in results]
        assert "Q_SHOOT_2004" in doc_ids, f"Expected Q_SHOOT_2004 in top results, got: {doc_ids}"

    def test_search_sailing_query(self, temp_index):
        results = temp_index.search("sailing 2016 women RS:X", top_k=3)
        doc_ids = [r["doc_id"] for r in results]
        assert "Q_SAILING_2016" in doc_ids

    def test_empty_query_returns_empty(self, temp_index):
        results = temp_index.search("", top_k=5)
        assert results == []

    def test_sanitize_query_removes_stopwords(self):
        result = sanitize_query_for_fts("how many events at the 2004 Summer Olympics had more than 37 competitors?")
        assert "many" not in result
        assert "the" not in result
        assert "2004" in result or "Summer" in result or "Olympics" in result


# ─── 3. Prompt Tests ─────────────────────────────────────────────────────────

class TestPrompt:
    def test_build_prompt_returns_two_messages(self):
        chunks = [{"chunk_id": "Q1#c0", "doc_id": "Q1", "title": "T", "chunk_type": "infobox", "content": "gold: Chen Ding"}]
        messages = build_rag_prompt("Who won gold?", chunks)
        assert len(messages) == 2

    def test_system_message_first(self):
        messages = build_rag_prompt("Test question?", [])
        assert messages[0]["role"] == "system"

    def test_user_message_contains_question(self):
        messages = build_rag_prompt("Who won gold in 2012?", [])
        user_msg = messages[1]["content"]
        assert "Who won gold in 2012?" in user_msg

    def test_user_message_contains_chunk_content(self):
        chunks = [{"chunk_id": "Q1#c0", "doc_id": "Q1", "title": "T", "chunk_type": "infobox", "content": "gold: Chen Ding"}]
        messages = build_rag_prompt("Who won?", chunks)
        user_msg = messages[1]["content"]
        assert "gold: Chen Ding" in user_msg

    def test_user_message_contains_chunk_id(self):
        chunks = [{"chunk_id": "Q1#c0", "doc_id": "Q1", "title": "T", "chunk_type": "infobox", "content": "Test content"}]
        messages = build_rag_prompt("Who won?", chunks)
        user_msg = messages[1]["content"]
        assert "Q1#c0" in user_msg

    def test_format_empty_chunks(self):
        text = format_context_chunks([])
        assert "No relevant context" in text


# ─── 4. MockLLM Tests ─────────────────────────────────────────────────────────

class TestMockLLM:
    def test_returns_llm_response(self):
        llm = MockLLM()
        messages = [{"role": "user", "content": "test"}]
        resp = llm.generate(messages)
        assert isinstance(resp, LLMResponse)

    def test_has_token_fields(self):
        llm = MockLLM()
        messages = [{"role": "user", "content": "test"}]
        resp = llm.generate(messages)
        assert resp.prompt_tokens > 0
        assert resp.completion_tokens > 0
        assert resp.total_tokens == resp.prompt_tokens + resp.completion_tokens

    def test_scripted_response_returned(self):
        llm = MockLLM(scripted_responses=["Custom scripted answer."])
        messages = [{"role": "user", "content": "test"}]
        resp = llm.generate(messages)
        assert resp.content == "Custom scripted answer."

    def test_scripted_queue(self):
        llm = MockLLM()
        llm.queue_response("First answer.")
        llm.queue_response("Second answer.")
        messages = [{"role": "user", "content": "Q"}]
        r1 = llm.generate(messages)
        r2 = llm.generate(messages)
        assert r1.content == "First answer."
        assert r2.content == "Second answer."

    def test_call_history_recorded(self):
        llm = MockLLM()
        messages = [{"role": "user", "content": "Q1"}]
        llm.generate(messages)
        assert len(llm.call_history) == 1


# ─── 5. Pipeline End-to-End Tests ────────────────────────────────────────────

class TestPipeline:
    @pytest.fixture
    def mini_pipeline(self, tmp_path):
        """A RAGPipeline using a small temp BM25 index with 3 docs."""
        import sqlite3
        from rag_only_pipeline.corpus.chunker import chunk_document

        db_path = tmp_path / "mini_rag.db"
        idx = BM25Index(db_path=db_path)

        docs = [
            {
                "doc_id": "Q_SHOOT_2004",
                "title": "Shooting at the 2004 Summer Olympics",
                "text": SAMPLE_DOC_TEXT
            },
            {
                "doc_id": "Q_SAIL_2016",
                "title": "Sailing at the 2016 Summer Olympics – Women's RS:X",
                "text": "[Infobox Olympic event]\n  event: Women RS:X\n  games: 2016 Summer\n  gold: Marina Alabau\n  goldNOC: ESP\n  nations: 26\n  competitors: 26\n\nThe sailing Women's RS:X took place at Marina da Gloria."
            }
        ]

        chunk_records, fts_records = [], []
        for doc in docs:
            chunks = chunk_document(doc["doc_id"], doc["title"], doc["text"])
            for c in chunks:
                chunk_records.append((c["chunk_id"], c["doc_id"], c["title"], c["chunk_type"], c["content"]))
                fts_records.append((c["chunk_id"], c["doc_id"], c["title"], c["content"]))

        with sqlite3.connect(str(db_path)) as conn:
            conn.executemany("INSERT INTO chunks VALUES (?,?,?,?,?)", chunk_records)
            conn.executemany("INSERT INTO chunks_fts VALUES (?,?,?,?)", fts_records)
            conn.commit()

        set_active_llm(MockLLM())
        return RAGPipeline(index=idx)

    def test_run_returns_rag_result(self, mini_pipeline):
        res = mini_pipeline.run("Who won gold in shooting 2004?", question_id="test-001")
        assert isinstance(res, RAGResult)

    def test_output_schema_complete(self, mini_pipeline):
        res = mini_pipeline.run("Who won gold in shooting 2004?", question_id="test-001")
        row = res.to_dict()
        required = {"question_id", "answer", "citations", "context_tokens", "input_tokens", "output_tokens", "total_tokens", "elapsed_time_s"}
        assert required.issubset(set(row.keys()))

    def test_question_id_in_output(self, mini_pipeline):
        res = mini_pipeline.run("Who won?", question_id="pub-001")
        assert res.to_dict()["question_id"] == "pub-001"

    def test_citations_is_list(self, mini_pipeline):
        res = mini_pipeline.run("Who won shooting 2004?", question_id="test-002")
        assert isinstance(res.to_dict()["citations"], list)

    def test_context_tokens_positive(self, mini_pipeline):
        res = mini_pipeline.run("Who won shooting 2004?", question_id="test-003")
        assert res.context_tokens > 0

    def test_elapsed_time_positive(self, mini_pipeline):
        res = mini_pipeline.run("Who won shooting 2004?", question_id="test-004")
        assert res.elapsed_time_s > 0

    def test_total_tokens_consistent(self, mini_pipeline):
        res = mini_pipeline.run("Who won shooting 2004?", question_id="test-005")
        assert res.total_tokens == res.input_tokens + res.output_tokens

    def test_jsonl_serializable(self, mini_pipeline):
        res = mini_pipeline.run("Who won shooting 2004?", question_id="test-006")
        row = res.to_dict()
        serialized = json.dumps(row)
        parsed = json.loads(serialized)
        assert parsed["question_id"] == "test-006"


# ─── 6. Citation Extraction Tests ─────────────────────────────────────────────

class TestCitationExtraction:
    @pytest.fixture
    def sample_chunks(self):
        return [
            {"chunk_id": "Q25239316#c0", "doc_id": "Q25239316", "title": "T1", "chunk_type": "infobox", "content": ""},
            {"chunk_id": "Q1050909#c1", "doc_id": "Q1050909", "title": "T2", "chunk_type": "text", "content": ""},
        ]

    def test_extracts_chunk_id_citation(self, sample_chunks):
        answer = "Naim was the winner [Q25239316#c0]."
        cits = extract_citations(answer, sample_chunks)
        assert "Q25239316#c0" in cits

    def test_extracts_doc_id_citation(self, sample_chunks):
        answer = "The gold was won [Q1050909]."
        cits = extract_citations(answer, sample_chunks)
        assert "Q1050909" in cits

    def test_ignores_unknown_ids(self, sample_chunks):
        answer = "According to [UNKNOWN123] something happened."
        cits = extract_citations(answer, sample_chunks)
        assert "UNKNOWN123" not in cits

    def test_fallback_to_first_chunk_when_no_citation(self, sample_chunks):
        answer = "This answer has no citation markers."
        cits = extract_citations(answer, sample_chunks)
        assert len(cits) > 0
        assert cits[0] == "Q25239316#c0"

    def test_no_duplicates(self, sample_chunks):
        answer = "See [Q25239316#c0] and also [Q25239316#c0] again."
        cits = extract_citations(answer, sample_chunks)
        assert cits.count("Q25239316#c0") == 1
