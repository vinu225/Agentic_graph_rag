"""Deterministic parser for Olympic event infoboxes and text.
Parses key attributes: event, games, venue, date, competitors, nations, medalists, etc.
"""

import re
from typing import Any, Dict, Optional


def parse_infobox(text: str) -> Dict[str, Any]:
    """Extract structured key-value pairs from [Infobox Olympic event] block."""
    info: Dict[str, Any] = {}
    if not text:
        return info

    infobox_match = re.search(r"\[Infobox Olympic event\](.*?)(?:\n\n|\Z)", text, re.DOTALL)
    if not infobox_match:
        return info

    raw_block = infobox_match.group(1)
    for line in raw_block.splitlines():
        line = line.strip()
        if not line or ":" not in line:
            continue
        key, val = line.split(":", 1)
        key = key.strip()
        val = val.strip()

        if key in ("competitors", "nations"):
            # Clean integers: e.g. "24" or "28 (from 16 nations)"
            digits = re.search(r"\b(\d+)\b", val)
            if digits:
                info[key] = int(digits.group(1))
            else:
                info[key] = None
        else:
            info[key] = val

    return info


def extract_sport_from_title(title: str) -> Optional[str]:
    """Extract sport name from standard Wikipedia Olympic title.
    Example: 'Canoeing at the 2012 Summer Olympics – Men\'s K-2 1000 metres' -> 'Canoeing'
    """
    if " at the " in title:
        return title.split(" at the ")[0].strip()
    return None


def extract_year_season_from_games(games_str: Optional[str]) -> Dict[str, Any]:
    """Parse '2012 Summer' into year 2012 and season 'Summer'."""
    res = {"year": None, "season": None}
    if not games_str:
        return res
    m = re.search(r"(\d{4})\s+(Summer|Winter)", games_str, re.IGNORECASE)
    if m:
        res["year"] = int(m.group(1))
        res["season"] = m.group(2).capitalize()
    return res
