"""Shared data models for odds and bet evaluation."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class BookmakerLine:
    """Line data for a single bookmaker."""

    bookmaker_key: str
    bookmaker_name: str
    spread_home: Optional[float] = None
    spread_away: Optional[float] = None
    total_over: Optional[float] = None
    total_under: Optional[float] = None
    home_moneyline: Optional[int] = None
    away_moneyline: Optional[int] = None


@dataclass(frozen=True)
class MultiBookLines:
    """Line data aggregated across multiple bookmakers."""

    sport: str
    home_team: str
    away_team: str
    books: dict[str, BookmakerLine]
