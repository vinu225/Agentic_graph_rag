"""Local SQLite implementation of GraphInterface.
Stores normalized Olympic events, infobox attributes, and chunks.
Implements get_events, get_event_attributes, count_or_rank, get_chunks.
"""

import re
import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

from agentic_pipeline.graph.base import GraphInterface


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


class SQLiteGraph(GraphInterface):
    """Local graph backend backed by an embedded SQLite database."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._conn = sqlite3.connect(self.db_path)
        self._conn.row_factory = sqlite3.Row
        self._init_schema()

    def _get_connection(self) -> sqlite3.Connection:
        return self._conn

    def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None

    def _init_schema(self) -> None:
        """Create normalized tables for events, attributes, and text chunks."""
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    doc_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    sport TEXT,
                    event_name TEXT,
                    games TEXT,
                    year INTEGER,
                    season TEXT,
                    venue TEXT,
                    date TEXT,
                    competitors INTEGER,
                    nations INTEGER,
                    gold TEXT,
                    goldNOC TEXT,
                    silver TEXT,
                    silverNOC TEXT,
                    bronze TEXT,
                    bronzeNOC TEXT,
                    prev_year INTEGER,
                    next_year INTEGER,
                    raw_infobox TEXT
                );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS doc_chunks (
                    chunk_id TEXT PRIMARY KEY,
                    doc_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    chunk_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    FOREIGN KEY(doc_id) REFERENCES events(doc_id)
                );
            """)
            # Fast index on frequently filtered fields
            cur.execute("CREATE INDEX IF NOT EXISTS idx_events_games ON events(games);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_events_sport ON events(sport);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_events_venue ON events(venue);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_events_year ON events(year);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_events_competitors ON events(competitors);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_chunks_doc ON doc_chunks(doc_id);")
            conn.commit()

    def upsert_event(self, event_data: Dict[str, Any], chunks: Optional[List[Dict[str, Any]]] = None) -> None:
        """Insert or update an event and its chunks."""
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT OR REPLACE INTO events (
                    doc_id, title, sport, event_name, games, year, season,
                    venue, date, competitors, nations, gold, goldNOC,
                    silver, silverNOC, bronze, bronzeNOC, prev_year, next_year, raw_infobox
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event_data.get("doc_id"),
                event_data.get("title"),
                event_data.get("sport"),
                event_data.get("event"),
                event_data.get("games"),
                event_data.get("year"),
                event_data.get("season"),
                event_data.get("venue"),
                event_data.get("date"),
                event_data.get("competitors"),
                event_data.get("nations"),
                event_data.get("gold"),
                event_data.get("goldNOC"),
                event_data.get("silver"),
                event_data.get("silverNOC"),
                event_data.get("bronze"),
                event_data.get("bronzeNOC"),
                event_data.get("prev"),
                event_data.get("next"),
                json.dumps(event_data.get("raw_infobox", {}))
            ))

            if chunks:
                for c in chunks:
                    cur.execute("""
                        INSERT OR REPLACE INTO doc_chunks (chunk_id, doc_id, title, chunk_type, content)
                        VALUES (?, ?, ?, ?, ?)
                    """, (c["chunk_id"], c["doc_id"], c["title"], c["chunk_type"], c["content"]))

            conn.commit()

    def get_events(
        self,
        games: Optional[str] = None,
        sport: Optional[str] = None,
        event_name: Optional[str] = None,
        venue: Optional[str] = None,
        date: Optional[str] = None,
        competitor_min: Optional[int] = None,
        competitor_max: Optional[int] = None,
        limit: int = 200,
    ) -> List[Dict[str, Any]]:
        """Filter and retrieve event entities with structured constraints."""
        # Auto-extract recognized sport names out of event_name if present
        if event_name:
            if not sport:
                for s in KNOWN_SPORTS:
                    if re.search(r"\b" + re.escape(s) + r"\b", event_name, re.IGNORECASE):
                        sport = s
                        event_name = re.sub(r"\b" + re.escape(s) + r"\b", "", event_name, flags=re.IGNORECASE).strip()
                        break
            else:
                event_name = re.sub(r"\b" + re.escape(sport) + r"\b", "", event_name, flags=re.IGNORECASE).strip()
            
            event_name = re.sub(r"^[–—\-\s,]+|[–—\-\s,]+$", "", event_name).strip() or None

        query = "SELECT * FROM events WHERE 1=1"
        params: List[Any] = []

        if games:
            query += " AND (games LIKE ? OR title LIKE ?)"
            params.extend([f"%{games}%", f"%{games}%"])
        if sport:
            query += " AND (sport LIKE ? OR title LIKE ?)"
            params.extend([f"%{sport}%", f"%{sport}%"])
        if event_name:
            query += " AND (event_name LIKE ? OR title LIKE ?)"
            params.extend([f"%{event_name}%", f"%{event_name}%"])
        if venue:
            query += " AND venue LIKE ?"
            params.append(f"%{venue}%")
        if date:
            query += " AND date LIKE ?"
            params.append(f"%{date}%")
        if competitor_min is not None:
            query += " AND competitors >= ?"
            params.append(competitor_min)
        if competitor_max is not None:
            query += " AND competitors <= ?"
            params.append(competitor_max)

        query += " LIMIT ?"
        params.append(limit)

        with self._get_connection() as conn:
            cur = conn.cursor()
            rows = cur.execute(query, params).fetchall()
            return [dict(r) for r in rows]

    def get_event_attributes(
        self,
        event_id_or_title: str,
        attributes: Optional[List[str]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Retrieve attributes for a specific event."""
        with self._get_connection() as conn:
            cur = conn.cursor()
            row = cur.execute("""
                SELECT * FROM events WHERE doc_id = ? OR title = ? OR title LIKE ? LIMIT 1
            """, (event_id_or_title, event_id_or_title, f"%{event_id_or_title}%")).fetchone()

            if not row:
                # General keyword fallback with apostrophe and symbol normalization
                clean_input = event_id_or_title.replace("’", "'").replace("–", "-").replace("—", "-")
                stop_words = {"at", "the", "in", "event", "of", "and", "or", "for", "to", "summer", "winter", "olympics"}
                tokens = clean_input.split()
                meaningful = []
                for t in tokens:
                    w = re.sub(r"^[^\w]+|[^\w]+$", "", t)
                    if w.lower() not in stop_words and len(w) >= 2:
                        # Normalize possessive / trailing 's (e.g. "women's" -> "women")
                        if w.lower().endswith("'s") and len(w) > 3:
                            meaningful.append(w[:-2])
                        else:
                            meaningful.append(w)
                
                # Also include year if present
                year_match = re.search(r"\b(19\d\d|20\d\d)\b", event_id_or_title)
                if year_match and year_match.group(1) not in meaningful:
                    meaningful.insert(0, year_match.group(1))

                if meaningful:
                    where_clauses = ["title LIKE ?" for _ in meaningful]
                    query = f"SELECT * FROM events WHERE {' AND '.join(where_clauses)} LIMIT 1"
                    params = [f"%{t}%" for t in meaningful]
                    row = cur.execute(query, params).fetchone()

            if not row:
                return None

            data = dict(row)
            if attributes:
                return {k: data[k] for k in attributes if k in data}
            return data

    def count_or_rank(
        self,
        events: List[Dict[str, Any]],
        metric: str = "competitors",
        operation: str = "count",
        threshold: Optional[float] = None,
        threshold_op: str = "gt",
        order: str = "desc",
        limit: int = 1,
        tie_breaker: str = "title_asc",
    ) -> Dict[str, Any]:
        """Execute deterministic numerical aggregation or ranking according to written contract."""
        if not events:
            return {"operation": operation, "metric": metric, "count": 0, "results": [], "tie_broken": False}

        # Filter out items with missing or non-numeric metric values
        valid_events = []
        for e in events:
            val = e.get(metric)
            if val is not None and isinstance(val, (int, float)):
                valid_events.append(e)

        if operation == "count":
            if threshold is None:
                matching = valid_events
            else:
                op_map = {
                    "gt": lambda v, t: v > t,
                    "gte": lambda v, t: v >= t,
                    "lt": lambda v, t: v < t,
                    "lte": lambda v, t: v <= t,
                    "eq": lambda v, t: v == t,
                }
                checker = op_map.get(threshold_op.lower(), op_map["gt"])
                matching = [e for e in valid_events if checker(e[metric], threshold)]

            count_val = len(matching)
            # Include matching events in results so model has count + entities in one call
            return {
                "operation": "count",
                "metric": metric,
                "count": count_val,
                "results": matching[:limit] if limit else matching,
                "tie_broken": False,
            }

        elif operation in ("max", "min", "top_k"):
            reverse_sort = (order.lower() == "desc") if operation == "top_k" else (operation == "max")

            # Deterministic primary sort by metric, secondary sort by title
            def sort_key(item: Dict[str, Any]):
                title_val = item.get("title", "")
                return item[metric]

            # Group items by metric score to detect ties
            sorted_items = sorted(
                valid_events,
                key=lambda x: (x[metric] if reverse_sort else -x[metric], x.get("title", "")),
                reverse=reverse_sort
            )

            # If reverse_sort: x[metric] descending, title ascending
            sorted_items = sorted(
                valid_events,
                key=lambda x: (-x[metric] if reverse_sort else x[metric], x.get("title", ""))
            )

            actual_limit = limit if operation == "top_k" else 1
            top_results = sorted_items[:actual_limit]

            # Detect if tie occurred
            tie_broken = False
            if len(sorted_items) > 1 and len(top_results) > 0:
                first_score = top_results[0][metric]
                # Check if second item has identical score
                if sorted_items[1][metric] == first_score:
                    tie_broken = True

            return {
                "operation": operation,
                "metric": metric,
                "count": len(top_results),
                "results": top_results,
                "tie_broken": tie_broken,
            }

        return {"error": f"Unknown operation {operation}"}

    def get_chunks(self, doc_id_or_title: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieve chunks for a document."""
        with self._get_connection() as conn:
            cur = conn.cursor()
            rows = cur.execute("""
                SELECT * FROM doc_chunks 
                WHERE doc_id = ? OR title = ? OR title LIKE ?
                ORDER BY chunk_id ASC LIMIT ?
            """, (doc_id_or_title, doc_id_or_title, f"%{doc_id_or_title}%", limit)).fetchall()
            return [dict(r) for r in rows]
