"""Async ESPN API client for NBA scoreboard data."""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from config import ESPN_BASE_URL

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class GameResult:
    """Structured game result data."""

    team: str
    opponent: str
    team_score: int
    opponent_score: int
    winner: bool
    total: int
    completed: bool
    status_detail: str
    period: int
    clock: Optional[str]


class ESPNClient:
    """Async client for ESPN NBA scoreboard API."""

    def __init__(self, timeout: float = 10.0):
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self) -> "ESPNClient":
        self._client = httpx.AsyncClient(timeout=httpx.Timeout(self.timeout))
        return self

    async def __aexit__(self, *_) -> None:
        if self._client:
            await self._client.aclose()

    @retry(
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.HTTPStatusError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=5),
        reraise=True,
    )
    async def _fetch_scoreboard(self, espn_date: str) -> dict:
        """Fetch scoreboard data from ESPN with retry logic."""
        if not self._client:
            raise RuntimeError("Client not initialized. Use async context manager.")

        url = f"{ESPN_BASE_URL}?dates={espn_date}"
        logger.info("Fetching ESPN scoreboard: %s", url)

        response = await self._client.get(url)
        response.raise_for_status()
        return response.json()

    async def fetch_game(
        self, team_text: str, date_str: str
    ) -> Optional[GameResult]:
        """Find a specific team's game on a given date.

        Args:
            team_text: Canonical team name (e.g. "New York Knicks")
            date_str: Date in MM/DD/YYYY format

        Returns:
            GameResult if found, None otherwise
        """
        try:
            date_obj = datetime.strptime(date_str, "%m/%d/%Y")
        except ValueError:
            logger.error("Invalid date string: %s", date_str)
            return None

        espn_date = date_obj.strftime("%Y%m%d")

        try:
            data = await self._fetch_scoreboard(espn_date)
        except httpx.TimeoutException:
            logger.error("ESPN API timed out after retries")
            raise ESPNError("ESPN is slow right now. Try again in a minute.")
        except httpx.HTTPStatusError as e:
            logger.error("ESPN API HTTP error: %s", e)
            raise ESPNError("Couldn't fetch scores. ESPN might be down.")

        events = data.get("events", [])
        if not events:
            logger.info("No games found for date %s", date_str)
            return None

        for event in events:
            competitions = event.get("competitions", [])
            if not competitions:
                continue

            competitors = competitions[0].get("competitors", [])
            if len(competitors) != 2:
                continue

            # Build team lookup
            teams = []
            for c in competitors:
                team_data = c.get("team", {})
                teams.append(
                    {
                        "name": team_data.get("displayName", ""),
                        "short_name": team_data.get("shortDisplayName", ""),
                        "abbreviation": team_data.get("abbreviation", ""),
                        "score": int(c.get("score", 0) or 0),
                        "winner": c.get("winner", False),
                    }
                )

            # Try to match team by display name, short name, or abbreviation
            team_lower = team_text.lower()
            for t in teams:
                names_to_check = [
                    t["name"].lower(),
                    t["short_name"].lower(),
                    t["abbreviation"].lower(),
                ]
                if any(team_lower == n or team_lower in n for n in names_to_check if n):
                    opponent = teams[0] if teams[1] == t else teams[1]

                    # Game status
                    status = event.get("status", {})
                    type_info = status.get("type", {})
                    completed = type_info.get("completed", False)
                    status_detail = type_info.get("description", "Unknown")
                    period = status.get("period", 0)
                    clock = status.get("displayClock")

                    return GameResult(
                        team=t["name"],
                        opponent=opponent["name"],
                        team_score=t["score"],
                        opponent_score=opponent["score"],
                        winner=t["winner"],
                        total=t["score"] + opponent["score"],
                        completed=completed,
                        status_detail=status_detail,
                        period=period,
                        clock=clock,
                    )

        logger.info("Team '%s' not found in games for %s", team_text, date_str)
        return None


class ESPNError(Exception):
    """Custom exception for ESPN API errors."""
    pass
