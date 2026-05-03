"""Async client for The Odds API — closing line value (CLV) lookup."""

import logging
from dataclasses import dataclass
from typing import Optional

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from config import ODDS_API_SPORTS

logger = logging.getLogger(__name__)

ODDS_API_BASE = "https://api.the-odds-api.com/v4/sports"


@dataclass(frozen=True)
class ClosingLine:
    """Closing line data from The Odds API."""

    sport: str
    home_team: str
    away_team: str
    spread_home: Optional[float] = None
    spread_away: Optional[float] = None
    total_over: Optional[float] = None
    total_under: Optional[float] = None
    home_moneyline: Optional[int] = None
    away_moneyline: Optional[int] = None
    bookmaker: Optional[str] = None


class OddsAPIClient:
    """Async client for The Odds API."""

    def __init__(self, api_key: str, timeout: float = 10.0):
        self.api_key = api_key
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self) -> "OddsAPIClient":
        self._client = httpx.AsyncClient(timeout=httpx.Timeout(self.timeout))
        return self

    async def __aexit__(self, *_) -> None:
        if self._client:
            await self._client.aclose()

    @retry(
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.HTTPStatusError)),
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=1, max=3),
        reraise=True,
    )
    async def _get(self, url: str, params: dict) -> dict:
        if not self._client:
            raise RuntimeError("Client not initialized. Use async context manager.")
        response = await self._client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    async def fetch_closing_line(
        self,
        sport: str,
        team: str,
        opponent: str,
        date_str: str,  # MM/DD/YYYY
    ) -> Optional[ClosingLine]:
        """Fetch the closing line for a specific game.

        Note: The Odds API free tier provides current/upcoming odds.
        Historical closing lines require a premium plan or caching
        previously fetched odds. This implementation attempts a best-effort
        lookup and gracefully degrades if data is unavailable.
        """
        odds_sport = ODDS_API_SPORTS.get(sport)
        if not odds_sport:
            logger.warning("No Odds API mapping for sport: %s", sport)
            return None

        url = f"{ODDS_API_BASE}/{odds_sport}/events"
        params = {
            "apiKey": self.api_key,
            "regions": "us",
            "markets": "h2h,spreads,totals",
            "oddsFormat": "american",
        }

        try:
            data = await self._get(url, params)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                logger.warning("Odds API authentication failed")
            elif e.response.status_code == 422:
                logger.warning("Odds API rate limit or quota exceeded")
            else:
                logger.error("Odds API HTTP error: %s", e)
            return None
        except Exception:
            logger.exception("Odds API request failed")
            return None

        if not isinstance(data, list):
            logger.warning("Unexpected Odds API response format")
            return None

        # Match event by team names
        team_lower = team.lower()
        opp_lower = opponent.lower()

        for event in data:
            home = event.get("home_team", "").lower()
            away = event.get("away_team", "").lower()

            # Check if this event matches our teams
            match = (
                (team_lower in home or team_lower in away)
                and (opp_lower in home or opp_lower in away)
            )
            if not match:
                continue

            # Extract lines from the first bookmaker
            bookmakers = event.get("bookmakers", [])
            if not bookmakers:
                continue

            bm = bookmakers[0]
            markets = {m["key"]: m for m in bm.get("markets", [])}

            spread_home = spread_away = None
            if "spreads" in markets:
                for outcome in markets["spreads"].get("outcomes", []):
                    if outcome["name"].lower() in home:
                        spread_home = float(outcome.get("point", 0))
                    elif outcome["name"].lower() in away:
                        spread_away = float(outcome.get("point", 0))

            total_over = total_under = None
            if "totals" in markets:
                for outcome in markets["totals"].get("outcomes", []):
                    if outcome["name"].lower() == "over":
                        total_over = float(outcome.get("point", 0))
                    elif outcome["name"].lower() == "under":
                        total_under = float(outcome.get("point", 0))

            home_ml = away_ml = None
            if "h2h" in markets:
                for outcome in markets["h2h"].get("outcomes", []):
                    if outcome["name"].lower() in home:
                        home_ml = int(outcome.get("price", 0))
                    elif outcome["name"].lower() in away:
                        away_ml = int(outcome.get("price", 0))

            return ClosingLine(
                sport=sport,
                home_team=event.get("home_team", ""),
                away_team=event.get("away_team", ""),
                spread_home=spread_home,
                spread_away=spread_away,
                total_over=total_over,
                total_under=total_under,
                home_moneyline=home_ml,
                away_moneyline=away_ml,
                bookmaker=bm.get("title"),
            )

        logger.info("No odds data found for %s vs %s", team, opponent)
        return None


class OddsAPIError(Exception):
    """Custom exception for Odds API errors."""
    pass
