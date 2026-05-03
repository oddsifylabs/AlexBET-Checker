"""SQLite cache for odds data to enable historical CLV lookups."""

import logging
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import Optional

from models import BookmakerLine, MultiBookLines

logger = logging.getLogger(__name__)

DEFAULT_DB_PATH = "odds_cache.db"

# How long cached entries remain valid before refetch is preferred
CACHE_TTL_HOURS = 24


class OddsCache:
    """Simple SQLite cache for sportsbook odds lines."""

    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        self._ensure_tables()

    @contextmanager
    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()

    def _ensure_tables(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS odds_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sport TEXT NOT NULL,
                    home_team TEXT NOT NULL,
                    away_team TEXT NOT NULL,
                    bookmaker_key TEXT NOT NULL,
                    bookmaker_name TEXT NOT NULL,
                    spread_home REAL,
                    spread_away REAL,
                    total_over REAL,
                    total_under REAL,
                    home_moneyline INTEGER,
                    away_moneyline INTEGER,
                    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(sport, home_team, away_team, bookmaker_key)
                )
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_odds_lookup
                ON odds_cache(sport, home_team, away_team, fetched_at)
                """
            )
            conn.commit()

    def get(
        self, sport: str, home_team: str, away_team: str
    ) -> Optional[MultiBookLines]:
        """Retrieve cached odds for a game if they exist and are fresh."""
        cutoff = datetime.utcnow() - timedelta(hours=CACHE_TTL_HOURS)
        cutoff_str = cutoff.isoformat()

        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT bookmaker_key, bookmaker_name, spread_home, spread_away,
                       total_over, total_under, home_moneyline, away_moneyline
                FROM odds_cache
                WHERE sport = ? AND home_team = ? AND away_team = ?
                  AND fetched_at > ?
                """,
                (sport, home_team, away_team, cutoff_str),
            ).fetchall()

        if not rows:
            return None

        books = {}
        for row in rows:
            (
                bm_key,
                bm_name,
                spread_home,
                spread_away,
                total_over,
                total_under,
                home_ml,
                away_ml,
            ) = row
            books[bm_key] = BookmakerLine(
                bookmaker_key=bm_key,
                bookmaker_name=bm_name,
                spread_home=spread_home,
                spread_away=spread_away,
                total_over=total_over,
                total_under=total_under,
                home_moneyline=home_ml,
                away_moneyline=away_ml,
            )

        return MultiBookLines(
            sport=sport,
            home_team=home_team,
            away_team=away_team,
            books=books,
        )

    def save(
        self, sport: str, home_team: str, away_team: str, multi_book: MultiBookLines
    ) -> None:
        """Store odds data in the cache."""
        with self._connect() as conn:
            for book in multi_book.books.values():
                conn.execute(
                    """
                    INSERT INTO odds_cache (
                        sport, home_team, away_team, bookmaker_key, bookmaker_name,
                        spread_home, spread_away, total_over, total_under,
                        home_moneyline, away_moneyline, fetched_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(sport, home_team, away_team, bookmaker_key)
                    DO UPDATE SET
                        bookmaker_name = excluded.bookmaker_name,
                        spread_home = excluded.spread_home,
                        spread_away = excluded.spread_away,
                        total_over = excluded.total_over,
                        total_under = excluded.total_under,
                        home_moneyline = excluded.home_moneyline,
                        away_moneyline = excluded.away_moneyline,
                        fetched_at = CURRENT_TIMESTAMP
                    """,
                    (
                        sport,
                        home_team,
                        away_team,
                        book.bookmaker_key,
                        book.bookmaker_name,
                        book.spread_home,
                        book.spread_away,
                        book.total_over,
                        book.total_under,
                        book.home_moneyline,
                        book.away_moneyline,
                    ),
                )
            conn.commit()

    def cleanup(self, days: int = 30) -> int:
        """Delete entries older than N days. Returns number of rows deleted."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        with self._connect() as conn:
            cursor = conn.execute(
                "DELETE FROM odds_cache WHERE fetched_at < ?",
                (cutoff.isoformat(),),
            )
            conn.commit()
            return cursor.rowcount
