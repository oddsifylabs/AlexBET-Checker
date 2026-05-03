"""Async client for The Odds API — closing line value (CLV) lookup."""

import logging
from typing import Optional

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from config import ODDS_API_BOOKMAKERS, ODDS_API_SPORTS
from models import BookmakerLine, MultiBookLines
from odds_cache import OddsCache

logger = logging.getLogger(__name__)

ODDS_API_BASE = "https://api.the-odds-api.com/v4/sports"


class OddsAPIClient:
    """Async client for The Odds API with local SQLite caching."""

    def __init__(self, api_key: str, timeout: float = 10.0, cache: Optional[OddsCache] = None):
        self.api_key = api_key
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None
        self._cache = cache or OddsCache()

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

    @staticmethod
    def _extract_markets(bookmaker: dict) -> dict[str, dict]:
        """Extract markets dict from a bookmaker entry."""
        markets = bookmaker.get("markets", [])
        return {m["key"]: m for m in markets}

    @staticmethod
    def _parse_spread(market: dict, home_team: str, away_team: str) -> tuple[Optional[float], Optional[float]]:
        """Parse spread market into (home_spread, away_spread)."""
        spread_home = spread_away = None
        for outcome in market.get("outcomes", []):
            name_lower = outcome["name"].lower()
            point = outcome.get("point")
            if point is None:
                continue
            if name_lower in home_team.lower():
                spread_home = float(point)
            elif name_lower in away_team.lower():
                spread_away = float(point)
        return spread_home, spread_away

    @staticmethod
    def _parse_total(market: dict) -> tuple[Optional[float], Optional[float]]:
        """Parse total market into (over_line, under_line)."""
        total_over = total_under = None
        for outcome in market.get("outcomes", []):
            name_lower = outcome["name"].lower()
            point = outcome.get("point")
            if point is None:
                continue
            if name_lower == "over":
                total_over = float(point)
            elif name_lower == "under":
                total_under = float(point)
        return total_over, total_under

    @staticmethod
    def _parse_moneyline(market: dict, home_team: str, away_team: str) -> tuple[Optional[int], Optional[int]]:
        """Parse moneyline market into (home_ml, away_ml)."""
        home_ml = away_ml = None
        for outcome in market.get("outcomes", []):
            name_lower = outcome["name"].lower()
            price = outcome.get("price")
            if price is None:
                continue
            if name_lower in home_team.lower():
                home_ml = int(price)
            elif name_lower in away_team.lower():
                away_ml = int(price)
        return home_ml, away_ml

    async def fetch_closing_lines(
        self,
        sport: str,
        team: str,
        opponent: str,
        date_str: str,  # MM/DD/YYYY — unused for now, kept for API consistency
    ) -> Optional[MultiBookLines]:
        """Fetch closing lines from multiple sportsbooks for a specific game.

        First checks the local SQLite cache. If not found or stale, queries
        The Odds API and stores the result for future historical lookups.
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
            "bookmakers": ",".join(ODDS_API_BOOKMAKERS),
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

            home_team = event.get("home_team", "")
            away_team = event.get("away_team", "")

            # Try cache first for freshness, but if we got API data, always update cache
            cached = self._cache.get(sport, home_team, away_team)

            books: dict[str, BookmakerLine] = {}

            for bm in event.get("bookmakers", []):
                bm_key = bm.get("key", "").lower()
                bm_title = bm.get("title", bm_key)
                if not bm_key:
                    continue

                markets = self._extract_markets(bm)

                spread_home = spread_away = None
                if "spreads" in markets:
                    spread_home, spread_away = self._parse_spread(
                        markets["spreads"], home_team, away_team
                    )

                total_over = total_under = None
                if "totals" in markets:
                    total_over, total_under = self._parse_total(markets["totals"])

                home_ml = away_ml = None
                if "h2h" in markets:
                    home_ml, away_ml = self._parse_moneyline(
                        markets["h2h"], home_team, away_team
                    )

                books[bm_key] = BookmakerLine(
                    bookmaker_key=bm_key,
                    bookmaker_name=bm_title,
                    spread_home=spread_home,
                    spread_away=spread_away,
                    total_over=total_over,
                    total_under=total_under,
                    home_moneyline=home_ml,
                    away_moneyline=away_ml,
                )

            if not books:
                logger.info("No bookmaker data found for %s vs %s", team, opponent)
                return cached  # fallback to stale cache if any

            result = MultiBookLines(
                sport=sport,
                home_team=home_team,
                away_team=away_team,
                books=books,
            )

            # Save to cache for future historical lookups
            try:
                self._cache.save(sport, home_team, away_team, result)
            except Exception:
                logger.exception("Failed to save odds to cache")

            return result

        # No live match found — try stale cache as fallback
        logger.info("No live odds data for %s vs %s, trying cache", team, opponent)
        return self._cache.get(sport, team, opponent) or self._cache.get(sport, opponent, team)


class OddsAPIError(Exception):
    """Custom exception for Odds API errors."""
    pass
