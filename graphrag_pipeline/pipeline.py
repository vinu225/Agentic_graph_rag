"""Pipeline 2: Minimal, Non-Agentic GraphRAG.

Performs exactly ONE retrieval step and ONE generation step:
1. Extracts filters from the question (games, sport, venue, date, competitor thresholds, event_name).
2. Queries the structured Knowledge Graph (SQLiteGraph) with extracted filters.
3. Retrieves narrative text chunks for top events via get_chunks.
4. If no graph entities match, falls back to BM25 text retrieval.
5. Combines structured graph evidence + narrative chunks into ONE prompt and calls OllamaLLM once.
"""

import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from agentic_pipeline.config import SQLITE_DB_PATH, DEFAULT_OLLAMA_MODEL
from agentic_pipeline.graph.sqlite_graph import SQLiteGraph
from agentic_pipeline.corpus.chronology import resolve_relative_games
from agentic_pipeline.llm_interface import OllamaLLM, LLMResponse
from rag_only_pipeline.retrieval.bm25_index import BM25Index


KNOWN_SPORTS = [
    "Alpine skiing", "Cross-country skiing", "Freestyle skiing", "Speed skating",
    "Figure skating", "Short track speed skating", "Ski jumping", "Nordic combined",
    "Biathlon", "Bobsleigh", "Skeleton", "Luge", "Curling", "Ice hockey",
    "Athletics", "Shooting", "Sailing", "Cycling", "Canoeing", "Fencing", "Judo",
    "Swimming", "Weightlifting", "Gymnastics", "Rowing", "Boxing", "Archery",
    "Badminton", "Table tennis", "Taekwondo", "Triathlon", "Equestrian",
    "Modern pentathlon", "Diving", "Synchronized swimming", "Water polo",
    "Volleyball", "Basketball", "Handball", "Football", "Hockey", "Tennis", "Wrestling"
]


SYSTEM_PROMPT = """You are a precise, factual Olympic Games research assistant equipped with a structured Knowledge Graph and document evidence.
Answer the question directly based solely on the provided Knowledge Graph data and narrative context chunks.

RULES:
1. Ground your answer in the provided evidence. Cite the relevant doc_id or chunk_id in square brackets (e.g. [Q47155365] or [Q1050909#c0]).
2. If a GRAPH AGGREGATION RESULT line is present in the context, your answer MUST state that exact number as the direct answer.
3. If a GRAPH RANKING RESULT line is present in the context, your answer MUST state that exact top-ranked event as the direct answer.
4. For winner/gold medalist questions, state the exact athlete or team name.
5. For nations or competitor count lookups, state the exact number directly from the event attributes.
6. Be concise, direct, and factual without conversational filler.
"""


@dataclass
class GraphRAGResult:
    question_id: str
    question: str
    answer: str
    citations: List[str]
    context_tokens: int
    input_tokens: int
    output_tokens: int
    total_tokens: int
    elapsed_time_s: float
    retrieved_events: int
    retrieved_chunks: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "question_id": self.question_id,
            "answer": self.answer,
            "citations": self.citations,
            "context_tokens": self.context_tokens,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.total_tokens,
            "elapsed_time_s": round(self.elapsed_time_s, 3),
        }


class GraphRAGPipeline:
    """Non-agentic single-retrieval, single-generation GraphRAG pipeline."""

    def __init__(
        self,
        db_path: Optional[str] = None,
        model_name: str = DEFAULT_OLLAMA_MODEL,
        llm: Optional[OllamaLLM] = None
    ):
        self.graph = SQLiteGraph(db_path or str(SQLITE_DB_PATH))
        self.bm25 = BM25Index()
        self.llm = llm or OllamaLLM(model_name=model_name)

    def extract_filters(self, question: str) -> Dict[str, Any]:
        """Extract structured query constraints from natural language question."""
        filters: Dict[str, Any] = {
            "games": None,
            "sport": None,
            "event_name": None,
            "venue": None,
            "date": None,
            "competitor_min": None,
            "competitor_max": None,
        }

        # 1. Games (relative or explicit)
        rel = resolve_relative_games(question)
        if rel and rel.get("resolved_games"):
            filters["games"] = rel["resolved_games"].replace(" Olympics", "").strip()
        else:
            m = re.search(r"(\d{4}\s+(?:Summer|Winter))", question, re.IGNORECASE)
            if m:
                filters["games"] = m.group(1).strip()

        # 2. Sport
        for s in KNOWN_SPORTS:
            if re.search(r"\b" + re.escape(s) + r"\b", question, re.IGNORECASE):
                filters["sport"] = s
                break

        # 3. Date
        dm = re.search(
            r"(\d{1,2}(?:–\d{1,2})?\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)(?:\s+\d{4})?)",
            question,
            re.IGNORECASE
        )
        if dm:
            filters["date"] = dm.group(1).strip()

        # 4. Venue
        vm = re.search(
            r"at\s+([A-Za-z0-9\s–—\-,]+?(?:Gymnasium|Stadium|Arena|Center|Centre|Pavilion\s*\d*|Velopark|Oval|Barracks|Hall|Park|Course))",
            question,
            re.IGNORECASE
        )
        if vm:
            filters["venue"] = vm.group(1).strip()

        # 5. Competitor Thresholds
        tm_gt = re.search(r"(?:more than|over|greater than)\s+(\d+)\s+competitors", question, re.IGNORECASE)
        if tm_gt:
            filters["competitor_min"] = int(tm_gt.group(1)) + 1

        tm_lt = re.search(r"(?:fewer than|less than|under)\s+(\d+)\s+competitors", question, re.IGNORECASE)
        if tm_lt:
            filters["competitor_max"] = int(tm_lt.group(1)) - 1

        # 6. Specific event name keywords (e.g. "women's 57 kg", "men's 20 kilometres walk", "Women's RS:X")
        em = re.search(
            r"(?:in|at)\s+(?:the\s+)?([A-Za-z0-9\s–—\-\'\"]+?)\s+(?:athletics|judo|swimming|biathlon|cycling|shooting|sailing|rowing|fencing|alpine skiing)?\s*event",
            question,
            re.IGNORECASE
        )
        if em:
            candidate_event = em.group(1).strip()
            # Clean generic words
            cleaned_event = re.sub(r"^(the|an|a)\s+", "", candidate_event, flags=re.IGNORECASE).strip()
            if len(cleaned_event) > 3:
                filters["event_name"] = cleaned_event

        return filters

    def run(self, question: str, question_id: Optional[str] = None) -> GraphRAGResult:
        """Execute one retrieval step and one generation step."""
        start_time = time.time()
        qid = question_id or "adhoc"

        # 1. Extract filters
        filters = self.extract_filters(question)

        # 2. Query Knowledge Graph
        events = self.graph.get_events(
            games=filters.get("games"),
            sport=filters.get("sport"),
            event_name=filters.get("event_name"),
            venue=filters.get("venue"),
            date=filters.get("date"),
            competitor_min=filters.get("competitor_min"),
            competitor_max=filters.get("competitor_max"),
            limit=50
        )

        # If zero events returned and event_name was set, retry without event_name filter
        # so we get the events in that sport/games edition
        if not events and filters.get("event_name"):
            events = self.graph.get_events(
                games=filters.get("games"),
                sport=filters.get("sport"),
                venue=filters.get("venue"),
                date=filters.get("date"),
                competitor_min=filters.get("competitor_min"),
                competitor_max=filters.get("competitor_max"),
                limit=50
            )

        # 3. Retrieve narrative text chunks
        chunks: List[Dict[str, Any]] = []
        if events:
            # Get chunks for up to 3 top matching events
            for e in events[:3]:
                ev_chunks = self.graph.get_chunks(e["doc_id"], limit=2)
                chunks.extend(ev_chunks)

            # Supplement with top-2 BM25 chunks for extra context
            supplementary = self.bm25.search(question, top_k=2)
            for sc in supplementary:
                if not any(c.get("chunk_id") == sc.get("chunk_id") for c in chunks):
                    chunks.append(sc)
        else:
            # Fallback entirely to BM25 if no graph filters or events matched
            chunks = self.bm25.search(question, top_k=8)

        # 4. Format Context Block
        context_parts: List[str] = []

        if events:
            ev_summary = [f"Found {len(events)} matching Knowledge Graph event entities:"]
            
            # Check for superlative / highest ranking
            if re.search(r"\b(highest|most|maximum|greatest)\s+(?:number\s+of\s+)?competitors\b", question, re.IGNORECASE):
                ranked = self.graph.count_or_rank(events, metric="competitors", operation="max")
                if ranked.get("results"):
                    top_e = ranked["results"][0]
                    ev_summary.append(f"GRAPH RANKING RESULT: Highest competitors event is [{top_e.get('doc_id')}] \"{top_e.get('title')}\" with {top_e.get('competitors')} competitors.")

            # Check for count / aggregation
            if re.search(r"\bhow\s+many\b", question, re.IGNORECASE) and filters.get("competitor_min") is not None:
                ev_summary.append(f"GRAPH AGGREGATION RESULT: Total count of events matching criteria is {len(events)}.")

            for idx, e in enumerate(events[:15], 1):
                ev_str = (
                    f"  {idx}. [{e.get('doc_id')}] Title: \"{e.get('title')}\" | "
                    f"Games: {e.get('games')} | Sport: {e.get('sport')} | Event: {e.get('event_name')} | "
                    f"Venue: {e.get('venue')} | Date: {e.get('date')} | "
                    f"Competitors: {e.get('competitors')} | Nations: {e.get('nations')} | "
                    f"Gold: {e.get('gold')} ({e.get('goldNOC')})"
                )
                ev_summary.append(ev_str)

            if len(events) > 15:
                ev_summary.append(f"  ... [and {len(events) - 15} more matching events]")

            context_parts.append("=== KNOWLEDGE GRAPH ENTITIES & ATTRIBUTES ===\n" + "\n".join(ev_summary))

        if chunks:
            chunk_summary = ["=== NARRATIVE TEXT CHUNKS ==="]
            for idx, c in enumerate(chunks[:6], 1):
                cid = c.get("chunk_id", "unknown")
                did = c.get("doc_id", "unknown")
                content = c.get("content", "").strip()
                chunk_summary.append(f"--- [CHUNK {idx}: {cid}] (Doc: {did}) ---\n{content}")
            context_parts.append("\n\n".join(chunk_summary))

        context_text = "\n\n".join(context_parts) if context_parts else "No relevant context found."
        context_tokens = max(1, len(context_text) // 4)

        # 5. Build prompt and generate single response
        user_message = (
            f"CONTEXT:\n{context_text}\n\n"
            f"QUESTION:\n{question}\n\n"
            f"ANSWER:"
        )

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ]

        llm_resp: LLMResponse = self.llm.generate(messages=messages, temperature=0.0)
        answer = llm_resp.content or "No answer could be determined from the context."

        # 6. Extract citations
        citations = []
        found_cits = re.findall(r"\[([A-Za-z0-9_#\-]+)\]", answer)
        candidate_ids = set()
        for e in events:
            if e.get("doc_id"):
                candidate_ids.add(e["doc_id"])
        for c in chunks:
            if c.get("chunk_id"):
                candidate_ids.add(c["chunk_id"])
            if c.get("doc_id"):
                candidate_ids.add(c["doc_id"])

        for cid in found_cits:
            if cid in candidate_ids and cid not in citations:
                citations.append(cid)

        # Fallback citation if model didn't bracket one explicitly
        if not citations:
            if events:
                citations = [events[0]["doc_id"]]
            elif chunks:
                citations = [chunks[0]["chunk_id"]]

        elapsed = time.time() - start_time

        return GraphRAGResult(
            question_id=qid,
            question=question,
            answer=answer,
            citations=citations,
            context_tokens=context_tokens,
            input_tokens=llm_resp.prompt_tokens,
            output_tokens=llm_resp.completion_tokens,
            total_tokens=llm_resp.total_tokens,
            elapsed_time_s=elapsed,
            retrieved_events=len(events),
            retrieved_chunks=len(chunks)
        )

    def close(self):
        if self.graph:
            self.graph.close()
