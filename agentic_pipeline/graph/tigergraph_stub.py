"""TigerGraph Savanna Backend Stub.
Implements the same GraphInterface.
Contains clear TODO slots to connect TigerGraph Cloud GSQL endpoints later.
"""

from typing import Any, Dict, List, Optional
from agentic_pipeline.graph.base import GraphInterface
from agentic_pipeline.config import (
    TG_HOST, TG_USERNAME, TG_PASSWORD, TG_SECRET, TG_GRAPH_NAME
)


class TigerGraphSavanna(GraphInterface):
    """TigerGraph Savanna implementation of GraphInterface.
    TODO: Fill with pyTigerGraph connection & installed queries in Step 7.
    """

    def __init__(
        self,
        host: str = TG_HOST,
        username: str = TG_USERNAME,
        password: str = TG_PASSWORD,
        secret: str = TG_SECRET,
        graphname: str = TG_GRAPH_NAME
    ):
        self.host = host
        self.username = username
        self.password = password
        self.secret = secret
        self.graphname = graphname
        # TODO: Initialize pyTigerGraph.TigerGraphConnection when credentials are provided
        self.conn = None

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
        # TODO: Call TigerGraph installed query (e.g. conn.runInstalledQuery("get_events_filtered", ...))
        raise NotImplementedError("TigerGraph Savanna backend will be connected in Step 7.")

    def get_event_attributes(
        self,
        event_id_or_title: str,
        attributes: Optional[List[str]] = None,
    ) -> Optional[Dict[str, Any]]:
        # TODO: Call TigerGraph query or getVertexByKey
        raise NotImplementedError("TigerGraph Savanna backend will be connected in Step 7.")

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
        # TODO: Run in GSQL or reuse deterministic client-side ranking over returned vertices
        raise NotImplementedError("TigerGraph Savanna backend will be connected in Step 7.")

    def get_chunks(self, doc_id_or_title: str, limit: int = 5) -> List[Dict[str, Any]]:
        # TODO: Fetch text chunks via TigerGraph edge or vector search
        raise NotImplementedError("TigerGraph Savanna backend will be connected in Step 7.")
