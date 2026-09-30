"""Deterministic Olympic Games Chronology Table and Relative Date Resolver.
Builds ordered sequences of Olympic Games editions to resolve relative-temporal phrases
(e.g., 'immediately before 2016' -> '2012 Summer Olympics').
"""

import re
from typing import Any, Dict, List, Optional, Tuple

# Official historical sequence of Modern Summer and Winter Olympics
SUMMER_OLYMPICS_CYCLE: List[Tuple[int, str]] = [
    (1988, "1988 Summer Olympics"),
    (1992, "1992 Summer Olympics"),
    (1996, "1996 Summer Olympics"),
    (2000, "2000 Summer Olympics"),
    (2004, "2004 Summer Olympics"),
    (2008, "2008 Summer Olympics"),
    (2012, "2012 Summer Olympics"),
    (2016, "2016 Summer Olympics"),
    (2020, "2020 Summer Olympics"),
]

WINTER_OLYMPICS_CYCLE: List[Tuple[int, str]] = [
    (1988, "1988 Winter Olympics"),
    (1992, "1992 Winter Olympics"),
    (1994, "1994 Winter Olympics"),
    (1998, "1998 Winter Olympics"),
    (2002, "2002 Winter Olympics"),
    (2006, "2006 Winter Olympics"),
    (2010, "2010 Winter Olympics"),
    (2014, "2014 Winter Olympics"),
    (2018, "2018 Winter Olympics"),
    (2022, "2022 Winter Olympics"),
]


def resolve_relative_games(query_text: str) -> Optional[Dict[str, Any]]:
    """Deterministically resolves phrases like:
    - 'Summer Olympics held immediately before 2016' -> '2012 Summer Olympics'
    - 'Winter Olympics held immediately before 2018' -> '2014 Winter Olympics'
    - 'Summer Olympics held immediately after 2004'  -> '2008 Summer Olympics'
    """
    is_winter = bool(re.search(r"\bwinter\b", query_text, re.IGNORECASE))
    cycle = WINTER_OLYMPICS_CYCLE if is_winter else SUMMER_OLYMPICS_CYCLE
    season = "Winter" if is_winter else "Summer"

    # Match 'immediately before YYYY' or 'prior to YYYY' or 'preceding YYYY'
    match_before = re.search(r"(?:immediately\s+before|prior\s+to|preceding)\s+(\d{4})", query_text, re.IGNORECASE)
    if match_before:
        target_year = int(match_before.group(1))
        # Find index of target_year
        years = [c[0] for c in cycle]
        if target_year in years:
            idx = years.index(target_year)
            if idx > 0:
                resolved_year, resolved_name = cycle[idx - 1]
                return {
                    "resolved_games": resolved_name,
                    "year": resolved_year,
                    "season": season,
                    "rule": f"Predecessor of {target_year} {season}"
                }

    # Match 'immediately after YYYY' or 'following YYYY'
    match_after = re.search(r"(?:immediately\s+after|following)\s+(\d{4})", query_text, re.IGNORECASE)
    if match_after:
        target_year = int(match_after.group(1))
        years = [c[0] for c in cycle]
        if target_year in years:
            idx = years.index(target_year)
            if idx + 1 < len(cycle):
                resolved_year, resolved_name = cycle[idx + 1]
                return {
                    "resolved_games": resolved_name,
                    "year": resolved_year,
                    "season": season,
                    "rule": f"Successor of {target_year} {season}"
                }

    # Match direct year reference if no relative pattern found (e.g. 'at the 2008 Summer Olympics')
    direct_match = re.search(r"\b(\d{4})\s+(Summer|Winter)\b", query_text, re.IGNORECASE)
    if direct_match:
        d_year = int(direct_match.group(1))
        d_season = direct_match.group(2).capitalize()
        return {
            "resolved_games": f"{d_year} {d_season} Olympics",
            "year": d_year,
            "season": d_season,
            "rule": "Direct mention"
        }

    return None
