"""Abstract Graph Interface.
Defines high-level methods for querying Olympic events and evidence.
No arbitrary SQL or GSQL queries are exposed.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class GraphInterface(ABC):
    """Abstract interface to be implemented by SQLite (locally) and TigerGraph (Savanna)."""

    @abstractmethod
    def get_events(
        self,
        games: Optional[str] = None,
        sport: Optional[str] = None,
        venue: Optional[str] = None,
        date: Optional[str] = None,
        competitor_min: Optional[int] = None,
        competitor_max: Optional[int] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Filter and retrieve event entities by attributes."""
        pass

    @abstractmethod
    def get_event_attributes(
        self,
        event_id_or_title: str,
        attributes: Optional[List[str]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Retrieve attributes (gold medal, date, venue, competitors, etc.) for a specific event."""
        pass

    @abstractmethod
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
        """Deterministic numerical aggregation, counting, or ranking over candidate events."""
        pass

    @abstractmethod
    def get_chunks(self, doc_id_or_title: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieve textual chunks associated with a document or event."""
        pass
