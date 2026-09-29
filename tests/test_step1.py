"""Tests for Step 1 components:
- Infobox parser
- Chunker
- Chronology / Relative Date Resolver
- SQLite Graph methods: get_events, get_event_attributes, count_or_rank (contract test cases), get_chunks.
"""

import sys
import os
import unittest
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agentic_pipeline.corpus.infobox_parser import parse_infobox, extract_sport_from_title
from agentic_pipeline.corpus.chunker import chunk_document
from agentic_pipeline.corpus.chronology import resolve_relative_games
from agentic_pipeline.graph.sqlite_graph import SQLiteGraph


class TestStep1Components(unittest.TestCase):

    def setUp(self):
        self.test_db = f"test_graph_{os.getpid()}_{id(self)}.db"
        self.graph = SQLiteGraph(self.test_db)

    def tearDown(self):
        if hasattr(self, 'graph') and self.graph:
            self.graph.close()
        if os.path.exists(self.test_db):
            try:
                os.remove(self.test_db)
            except Exception:
                pass

    def test_infobox_parser(self):
        sample_text = """[Infobox Olympic event]
  event: Men's canoe sprint K-2 1,000 metres
  games: 2012 Summer
  venue: Eton Dorney
  date: 6 to 8 August
  competitors: 24
  nations: 12
  gold: Rudolf DombiRoland Kökény
  goldNOC: HUN
  prev: 2008
  next: 2016

The men's canoe sprint competition..."""
        info = parse_infobox(sample_text)
        self.assertEqual(info.get("games"), "2012 Summer")
        self.assertEqual(info.get("competitors"), 24)
        self.assertEqual(info.get("nations"), 12)
        self.assertEqual(info.get("gold"), "Rudolf DombiRoland Kökény")

    def test_relative_date_resolver(self):
        # 1. Immediately before 2016 (Summer) -> 2012 Summer Olympics
        res1 = resolve_relative_games("Who won the gold medal at the Summer Olympics held immediately before 2016?")
        self.assertIsNotNone(res1)
        self.assertEqual(res1["resolved_games"], "2012 Summer Olympics")
        self.assertEqual(res1["year"], 2012)

        # 2. Immediately before 2020 (Summer) -> 2016 Summer Olympics
        res2 = resolve_relative_games("held immediately before 2020")
        self.assertIsNotNone(res2)
        self.assertEqual(res2["resolved_games"], "2016 Summer Olympics")
        self.assertEqual(res2["year"], 2016)

        # 3. Direct mention
        res3 = resolve_relative_games("shooting events at the 2004 Summer Olympics")
        self.assertIsNotNone(res3)
        self.assertEqual(res3["resolved_games"], "2004 Summer Olympics")

    def test_chunker(self):
        doc_id = "Q303623"
        title = "Canoeing at the 2012 Summer Olympics – Men's K-2 1000 metres"
        text = """[Infobox Olympic event]
  event: Men's canoe sprint K-2 1,000 metres
  games: 2012 Summer
  competitors: 24

First paragraph describing the event.

Second paragraph with more competition details."""
        chunks = chunk_document(doc_id, title, text)
        self.assertTrue(len(chunks) >= 2)
        self.assertEqual(chunks[0]["chunk_type"], "infobox")
        self.assertEqual(chunks[0]["chunk_id"], f"{doc_id}#c0")

    def test_count_or_rank_contract_examples(self):
        # Insert mock events
        events_data = [
            {"doc_id": "e1", "title": "Shooting Men 10m", "competitors": 45, "sport": "Shooting", "games": "2004 Summer"},
            {"doc_id": "e2", "title": "Shooting Women 10m", "competitors": 38, "sport": "Shooting", "games": "2004 Summer"},
            {"doc_id": "e3", "title": "Shooting Trap", "competitors": 30, "sport": "Shooting", "games": "2004 Summer"},
            {"doc_id": "e4", "title": "Shooting Skeet", "competitors": None, "sport": "Shooting", "games": "2004 Summer"}, # missing field
            {"doc_id": "e5", "title": "Archery Team", "competitors": 16, "sport": "Archery", "games": "2004 Summer"},
            {"doc_id": "e6", "title": "Badminton Doubles", "competitors": 16, "sport": "Badminton", "games": "2004 Summer"}, # exact tie
        ]
        for e in events_data:
            self.graph.upsert_event(e)

        # Example 1: Count with threshold > 37
        shooting_events = self.graph.get_events(sport="Shooting")
        c_res = self.graph.count_or_rank(
            shooting_events,
            metric="competitors",
            operation="count",
            threshold=37,
            threshold_op="gt"
        )
        # e1 (45) and e2 (38) > 37. e3 (30) is not. e4 (None) is excluded.
        self.assertEqual(c_res["count"], 2)
        self.assertEqual(c_res["operation"], "count")

        # Example 2: Superlative Max
        max_res = self.graph.count_or_rank(
            shooting_events,
            metric="competitors",
            operation="max"
        )
        self.assertEqual(max_res["count"], 1)
        self.assertEqual(max_res["results"][0]["title"], "Shooting Men 10m")
        self.assertEqual(max_res["results"][0]["competitors"], 45)

        # Example 3: Missing field test
        # e4 has competitors=None, verify it was safely ignored in count & max
        self.assertNotIn("Shooting Skeet", [r.get("title") for r in max_res["results"]])

        # Example 4: Top-1 with exact tie-breaking (Archery vs Badminton both 16)
        tie_events = [events_data[4], events_data[5]]
        top_tie = self.graph.count_or_rank(
            tie_events,
            metric="competitors",
            operation="top_k",
            limit=1,
            tie_breaker="title_asc"
        )
        self.assertEqual(top_tie["count"], 1)
        self.assertEqual(top_tie["results"][0]["title"], "Archery Team")
        self.assertTrue(top_tie["tie_broken"])


if __name__ == "__main__":
    unittest.main()
