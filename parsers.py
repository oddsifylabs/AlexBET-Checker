"""Message parsing and validation utilities."""

import logging
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Optional

from config import SPORT_ALIASES, TEAM_ALIASES

logger = logging.getLogger(__name__)

# Date patterns: MM/DD/YYYY, M/D/YYYY, MM-DD-YYYY, etc.
_DATE_PATTERN = re.compile(r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{4})\b")

# Spread pattern: +3.5, -7, +10, etc.
_SPREAD_PATTERN = re.compile(r"([+-]\d+\.?\d*)")

# Total pattern: O 220.5, U 215, Over 200, Under 9.5, etc.
_TOTAL_PATTERN = re.compile(r"\b(O|U|Over|Under)\s+(\d+\.?\d*)\b", re.IGNORECASE)

# VS pattern to extract two teams
_VS_PATTERN = re.compile(r"\b(vs\.?|versus|at|@)\b", re.IGNORECASE)


@dataclass(frozen=True)
class BetRequest:
    """Parsed bet request from user message."""

    team: str
    date: str
    sport: str = "nba"  # default sport
    bet_type: Literal["moneyline", "spread", "total"] = "moneyline"
    line: Optional[float] = None
    total_side: Optional[Literal["over", "under"]] = None
    opponent: Optional[str] = None


def _detect_sport(text: str) -> tuple[str, str]:
    """Detect sport keyword at the start of text. Returns (sport_key, cleaned_text)."""
    lowered = text.lower().strip()
    words = lowered.split()
    if not words:
        return "nba", text

    # Check first word + first two words
    first_word = words[0]
    first_two = " ".join(words[:2]) if len(words) >= 2 else first_word

    for alias, sport_key in SPORT_ALIASES.items():
        if first_two == alias or first_word == alias:
            # Remove the sport keyword from text
            if first_two == alias:
                cleaned = " ".join(words[2:])
            else:
                cleaned = " ".join(words[1:])
            return sport_key, cleaned

    return "nba", text


def normalize_team(raw_team: str) -> str:
    """Normalize a raw team string using aliases."""
    cleaned = raw_team.strip().lower()
    # Direct alias match
    if cleaned in TEAM_ALIASES:
        return TEAM_ALIASES[cleaned]
    # Partial alias match (e.g. "Lakers" -> "Los Angeles Lakers")
    for alias, canonical in TEAM_ALIASES.items():
        if cleaned in alias or alias in cleaned:
            return canonical
    # Return title-cased original as fallback
    return raw_team.strip().title()


def _extract_teams(team_raw: str) -> tuple[str, Optional[str]]:
    """Extract primary team and optional opponent from text."""
    match = _VS_PATTERN.search(team_raw)
    if match:
        left = team_raw[: match.start()].strip()
        right = team_raw[match.end() :].strip()
        if left and right:
            return normalize_team(left), normalize_team(right)
    return normalize_team(team_raw), None


def parse_message(text: str) -> Optional[BetRequest]:
    """Extract bet details from a user message.

    Returns BetRequest or None on failure.
    """
    if not text:
        return None

    # Detect sport first
    sport, text_no_sport = _detect_sport(text)

    # Extract date
    date_match = _DATE_PATTERN.search(text_no_sport)
    if not date_match:
        return None

    date_str = date_match.group(1).replace("-", "/")
    remaining = text_no_sport.replace(date_match.group(0), "").strip()

    if not remaining:
        return None

    # Check for total pattern first (O/U)
    total_match = _TOTAL_PATTERN.search(remaining)
    if total_match:
        side_raw = total_match.group(1).upper()
        total_line = float(total_match.group(2))
        total_side = "over" if side_raw in ("O", "OVER") else "under"
        # Remove total pattern from remaining text
        remaining = (
            remaining[: total_match.start()] + remaining[total_match.end() :]
        ).strip()
        team, opponent = _extract_teams(remaining)
        if not team:
            return None
        return BetRequest(
            team=team,
            date=date_str,
            sport=sport,
            bet_type="total",
            line=total_line,
            total_side=total_side,
            opponent=opponent,
        )

    # Check for spread pattern
    spread_match = _SPREAD_PATTERN.search(remaining)
    if spread_match:
        spread_line = float(spread_match.group(1))
        # Remove spread from remaining text
        remaining = (
            remaining[: spread_match.start()] + remaining[spread_match.end() :]
        ).strip()
        team, opponent = _extract_teams(remaining)
        if not team:
            return None
        return BetRequest(
            team=team,
            date=date_str,
            sport=sport,
            bet_type="spread",
            line=spread_line,
            opponent=opponent,
        )

    # Default: moneyline
    team, opponent = _extract_teams(remaining)
    if not team:
        return None
    return BetRequest(
        team=team,
        date=date_str,
        sport=sport,
        bet_type="moneyline",
        opponent=opponent,
    )


def validate_date(date_str: str) -> Optional[datetime]:
    """Validate and parse a date string. Returns datetime or None."""
    try:
        dt = datetime.strptime(date_str, "%m/%d/%Y")
        # Reject future dates more than ~1 year ahead
        now = datetime.now()
        if dt.year > now.year + 1:
            logger.warning("Date %s is too far in the future", date_str)
            return None
        return dt
    except ValueError:
        logger.warning("Invalid date format: %s", date_str)
        return None
