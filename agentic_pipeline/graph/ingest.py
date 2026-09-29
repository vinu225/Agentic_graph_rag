"""Build and ingest the local SQLite graph from the hackathon corpus.
Can ingest a subset or the full 2,951 documents.
"""

import time
from pathlib import Path
from typing import Optional

from agentic_pipeline.config import CORPUS_PATH, SQLITE_DB_PATH
from agentic_pipeline.corpus.loader import stream_corpus
from agentic_pipeline.corpus.infobox_parser import (
    parse_infobox,
    extract_sport_from_title,
    extract_year_season_from_games,
)
from agentic_pipeline.corpus.chunker import chunk_document
from agentic_pipeline.graph.sqlite_graph import SQLiteGraph


def ingest_corpus_to_sqlite(
    corpus_file: Optional[Path] = None,
    db_file: Optional[Path] = None,
    max_docs: Optional[int] = None,
    verbose: bool = True
) -> SQLiteGraph:
    """Read corpus JSONL and ingest into SQLite database."""
    target_corpus = corpus_file or CORPUS_PATH
    target_db = str(db_file or SQLITE_DB_PATH)

    graph = SQLiteGraph(target_db)
    count = 0
    t0 = time.time()

    if verbose:
        print(f"Starting ingestion from: {target_corpus}")
        print(f"Target SQLite database: {target_db}")

    for doc in stream_corpus(target_corpus):
        doc_id = doc.get("doc_id")
        title = doc.get("title", "")
        text = doc.get("text", "")

        infobox = parse_infobox(text)
        sport = extract_sport_from_title(title)
        games = infobox.get("games")
        year_season = extract_year_season_from_games(games)

        event_record = {
            "doc_id": doc_id,
            "title": title,
            "sport": sport,
            "event": infobox.get("event"),
            "games": games,
            "year": year_season.get("year"),
            "season": year_season.get("season"),
            "venue": infobox.get("venue"),
            "date": infobox.get("date"),
            "competitors": infobox.get("competitors"),
            "nations": infobox.get("nations"),
            "gold": infobox.get("gold"),
            "goldNOC": infobox.get("goldNOC"),
            "silver": infobox.get("silver"),
            "silverNOC": infobox.get("silverNOC"),
            "bronze": infobox.get("bronze"),
            "bronzeNOC": infobox.get("bronzeNOC"),
            "prev": infobox.get("prev"),
            "next": infobox.get("next"),
            "raw_infobox": infobox
        }

        # Generate text chunks
        chunks = chunk_document(doc_id, title, text)

        graph.upsert_event(event_record, chunks)
        count += 1

        if verbose and count % 500 == 0:
            print(f"  Ingested {count} documents ({time.time() - t0:.2f}s)...")

        if max_docs and count >= max_docs:
            break

    elapsed = time.time() - t0
    if verbose:
        print(f"Completed ingestion: {count} documents in {elapsed:.2f}s.")

    return graph


if __name__ == "__main__":
    ingest_corpus_to_sqlite()
