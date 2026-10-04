"""Specialized tools for the Agentic GraphRAG orchestrator.
Each tool provides a concrete, high-level capability:
- link_entities: Entity and relative temporal resolution
- get_events: Structured graph attribute filtering
- get_event_attributes: Detailed event fields
- count_or_rank: Deterministic numerical aggregations & rankings
- retrieve_chunks: Unstructured text chunk retrieval
- evaluate_evidence: Verification of collected evidence against question requirements
"""

from typing import Any, Dict, List, Optional
from agentic_pipeline.graph.base import GraphInterface
from agentic_pipeline.corpus.chronology import resolve_relative_games


class ToolSuite:
    """Encapsulates tool definitions and binds them to the underlying GraphInterface."""

    def __init__(self, graph: GraphInterface):
        self.graph = graph

    # 1. link_entities
    def link_entities(self, query: str) -> Dict[str, Any]:
        """Resolves relative dates (e.g. 'immediately before 2016' -> '2012 Summer Olympics')
        and extracts candidate sports and key terms.
        """
        temporal_resolution = resolve_relative_games(query)

        # Detect candidate sport mentions
        known_sports = [
            "Biathlon", "Athletics", "Shooting", "Sailing", "Cycling",
            "Canoeing", "Fencing", "Judo", "Swimming", "Weightlifting",
            "Gymnastics", "Rowing", "Boxing", "Archery", "Badminton"
        ]
        detected_sports = [s for s in known_sports if s.lower() in query.lower()]

        return {
            "temporal_resolution": temporal_resolution,
            "detected_sports": detected_sports,
            "query": query
        }

    # 2. get_events
    def get_events(
        self,
        games: Optional[str] = None,
        sport: Optional[str] = None,
        event_name: Optional[str] = None,
        venue: Optional[str] = None,
        date: Optional[str] = None,
        competitor_min: Optional[int] = None,
        competitor_max: Optional[int] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Retrieve events matching criteria from the graph."""
        return self.graph.get_events(
            games=games,
            sport=sport,
            event_name=event_name,
            venue=venue,
            date=date,
            competitor_min=competitor_min,
            competitor_max=competitor_max,
            limit=limit
        )

    # 3. get_event_attributes
    def get_event_attributes(
        self,
        event_id_or_title: str,
        attributes: Optional[List[str]] = None
    ) -> Optional[Dict[str, Any]]:
        """Retrieve specific fields (gold medalist, competitors, venue, etc.) for an event."""
        return self.graph.get_event_attributes(event_id_or_title, attributes)

    # 4. count_or_rank
    def count_or_rank(
        self,
        events: List[Dict[str, Any]],
        metric: str = "competitors",
        operation: str = "count",
        threshold: Optional[float] = None,
        threshold_op: str = "gt",
        order: str = "desc",
        limit: int = 1,
        tie_breaker: str = "title_asc"
    ) -> Dict[str, Any]:
        """Compute numerical counts or ranked lists over candidate events."""
        return self.graph.count_or_rank(
            events=events,
            metric=metric,
            operation=operation,
            threshold=threshold,
            threshold_op=threshold_op,
            order=order,
            limit=limit,
            tie_breaker=tie_breaker
        )

    # 5. retrieve_chunks
    def retrieve_chunks(self, doc_id_or_title: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieve unstructured text chunks for a document."""
        return self.graph.get_chunks(doc_id_or_title, limit=limit)

    # 6. evaluate_evidence
    def evaluate_evidence(
        self,
        question: str,
        evidence: List[Dict[str, Any]],
        required_slots: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Check whether gathered evidence is sufficient to answer the question."""
        valid_evidence = []
        for e in evidence:
            tool = e.get("tool") or e.get("type")
            output = e.get("output")
            if not output:
                continue

            if tool == "get_events":
                if isinstance(output, dict) and output.get("returned_count", 0) > 0:
                    valid_evidence.append(e)
                elif isinstance(output, list) and len(output) > 0:
                    valid_evidence.append(e)
            elif tool == "count_or_rank":
                if isinstance(output, dict) and (output.get("results") or output.get("count") is not None):
                    valid_evidence.append(e)
            elif tool == "get_event_attributes":
                if isinstance(output, dict) and (output.get("doc_id") or output.get("title")):
                    valid_evidence.append(e)
            elif tool == "retrieve_chunks":
                if isinstance(output, list) and len(output) > 0:
                    valid_evidence.append(e)

        sufficient = len(valid_evidence) > 0
        missing = [] if sufficient else (required_slots or ["event_data"])
        return {
            "sufficient": sufficient,
            "missing_slots": missing,
            "evidence_count": len(valid_evidence)
        }

    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """Return OpenAI-compatible JSON tool schemas for LLM tool calling."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "link_entities",
                    "description": "Resolves relative dates (e.g. 'immediately before 2016' -> '2012 Summer') and extracts candidate sports from the question.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "The user question or temporal/entity phrase to resolve."}
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_events",
                    "description": "Filters Olympic events by games edition, sport, event name, venue, date, or competitor bounds. Each event has a canonical 'title' (e.g. 'Sailing at the 2000 Summer Olympics – Soling') and 'event_name' subdiscipline.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "games": {"type": "string", "description": "e.g. '2004 Summer', '2012 Summer', '2018 Winter'"},
                            "sport": {"type": "string", "description": "Sport name, e.g. 'Shooting', 'Biathlon', 'Athletics'"},
                            "event_name": {"type": "string", "description": "Specific event name, e.g. 'men\'s 20 kilometres walk', 'Women\'s RS:X'"},
                            "venue": {"type": "string", "description": "Venue name, e.g. 'Olympic Weightlifting Gymnasium'"},
                            "date": {"type": "string", "description": "Specific date, e.g. '20 September 1988'"},
                            "competitor_min": {"type": "integer"},
                            "competitor_max": {"type": "integer"},
                            "limit": {"type": "integer", "default": 100}
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_event_attributes",
                    "description": "Retrieves attributes (gold, silver, bronze medalists, competitors, venue, etc.) for a specific event title or doc_id.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "event_id_or_title": {"type": "string", "description": "Event doc_id or full/partial title"}
                        },
                        "required": ["event_id_or_title"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "count_or_rank",
                    "description": "Performs deterministic counts or rankings (highest/lowest/top-k) on retrieved events. Returns ranked events with their canonical 'title' and competitor/nation metrics.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "metric": {"type": "string", "enum": ["competitors", "nations"], "default": "competitors"},
                            "operation": {"type": "string", "enum": ["count", "max", "min", "top_k"], "default": "count"},
                            "threshold": {"type": "number", "description": "Value to compare against for count operations"},
                            "threshold_op": {"type": "string", "enum": ["gt", "gte", "lt", "lte", "eq"], "default": "gt"},
                            "limit": {"type": "integer", "default": 1}
                        },
                        "required": ["operation"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "retrieve_chunks",
                    "description": "Retrieves textual chunks from the document for unstructured narrative facts.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "doc_id_or_title": {"type": "string", "description": "Document ID or title"}
                        },
                        "required": ["doc_id_or_title"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "evaluate_evidence",
                    "description": "Evaluates whether current evidence conclusively answers the question.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "question": {"type": "string"}
                        },
                        "required": ["question"]
                    }
                }
            }
        ]
