"""Message parsing and validation utilities."""

import logging
import re
from datetime import datetime
from typing import Optional

from config import TEAM_ALIASES

logger = logging.getLogger(__name__)

# Date patterns: MM/DD/YYYY, M/D/YYYY, MM-DD-YYYY, etc.
_DATE_PATTERN = re.compile(r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{4})\b")


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


def parse_message(text: str) -> tuple[Optional[str], Optional[str]]:
    """Extract team name and date from a user message.

    Returns (canonical_team_name, date_str) or (None, None) on failure.
    """
    if not text:
        return None, None

    date_match = _DATE_PATTERN.search(text)
    if not date_match:
        return None, None

    date_str = date_match.group(1).replace("-", "/")
    team_raw = text.replace(date_match.group(0), "").strip()

    if not team_raw:
        return None, None

    team = normalize_team(team_raw)
    return team, date_str


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
