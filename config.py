"""Configuration and constants for the Telegram Bet Bot."""

import os
from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True)
class Config:
    """Bot configuration loaded from environment variables."""

    telegram_token: str
    espn_timeout: float = 10.0
    max_requests_per_minute: int = 10
    log_level: str = "INFO"

    @classmethod
    def from_env(cls) -> "Config":
        token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        if not token:
            raise ValueError(
                "Missing TELEGRAM_BOT_TOKEN environment variable. "
                "Set it before running the bot."
            )
        return cls(
            telegram_token=token,
            espn_timeout=float(os.getenv("ESPN_TIMEOUT", "10.0")),
            max_requests_per_minute=int(os.getenv("MAX_REQUESTS_PER_MINUTE", "10")),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )


# ESPN API constants
ESPN_BASE_URL: Final[str] = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"

# Comprehensive team aliases for fuzzy matching
TEAM_ALIASES: Final[dict[str, str]] = {
    # Eastern Conference
    "atlanta hawks": "Atlanta Hawks",
    "hawks": "Atlanta Hawks",
    "atl": "Atlanta Hawks",
    "atlanta": "Atlanta Hawks",
    "boston celtics": "Boston Celtics",
    "celtics": "Boston Celtics",
    "bos": "Boston Celtics",
    "boston": "Boston Celtics",
    "brooklyn nets": "Brooklyn Nets",
    "nets": "Brooklyn Nets",
    "bkn": "Brooklyn Nets",
    "brooklyn": "Brooklyn Nets",
    "charlotte hornets": "Charlotte Hornets",
    "hornets": "Charlotte Hornets",
    "cha": "Charlotte Hornets",
    "charlotte": "Charlotte Hornets",
    "chicago bulls": "Chicago Bulls",
    "bulls": "Chicago Bulls",
    "chi": "Chicago Bulls",
    "chicago": "Chicago Bulls",
    "cleveland cavaliers": "Cleveland Cavaliers",
    "cavaliers": "Cleveland Cavaliers",
    "cavs": "Cleveland Cavaliers",
    "cle": "Cleveland Cavaliers",
    "cleveland": "Cleveland Cavaliers",
    "detroit pistons": "Detroit Pistons",
    "pistons": "Detroit Pistons",
    "det": "Detroit Pistons",
    "detroit": "Detroit Pistons",
    "indiana pacers": "Indiana Pacers",
    "pacers": "Indiana Pacers",
    "ind": "Indiana Pacers",
    "indiana": "Indiana Pacers",
    "miami heat": "Miami Heat",
    "heat": "Miami Heat",
    "mia": "Miami Heat",
    "miami": "Miami Heat",
    "milwaukee bucks": "Milwaukee Bucks",
    "bucks": "Milwaukee Bucks",
    "mil": "Milwaukee Bucks",
    "milwaukee": "Milwaukee Bucks",
    "new york knicks": "New York Knicks",
    "knicks": "New York Knicks",
    "ny": "New York Knicks",
    "nyk": "New York Knicks",
    "new york": "New York Knicks",
    "orlando magic": "Orlando Magic",
    "magic": "Orlando Magic",
    "orl": "Orlando Magic",
    "orlando": "Orlando Magic",
    "philadelphia 76ers": "Philadelphia 76ers",
    "76ers": "Philadelphia 76ers",
    "sixers": "Philadelphia 76ers",
    "phi": "Philadelphia 76ers",
    "philadelphia": "Philadelphia 76ers",
    "toronto raptors": "Toronto Raptors",
    "raptors": "Toronto Raptors",
    "tor": "Toronto Raptors",
    "toronto": "Toronto Raptors",
    "washington wizards": "Washington Wizards",
    "wizards": "Washington Wizards",
    "was": "Washington Wizards",
    "washington": "Washington Wizards",
    # Western Conference
    "dallas mavericks": "Dallas Mavericks",
    "mavericks": "Dallas Mavericks",
    "mavs": "Dallas Mavericks",
    "dal": "Dallas Mavericks",
    "dallas": "Dallas Mavericks",
    "denver nuggets": "Denver Nuggets",
    "nuggets": "Denver Nuggets",
    "den": "Denver Nuggets",
    "denver": "Denver Nuggets",
    "golden state warriors": "Golden State Warriors",
    "warriors": "Golden State Warriors",
    "gsw": "Golden State Warriors",
    "golden state": "Golden State Warriors",
    "gs": "Golden State Warriors",
    "houston rockets": "Houston Rockets",
    "rockets": "Houston Rockets",
    "hou": "Houston Rockets",
    "houston": "Houston Rockets",
    "la clippers": "LA Clippers",
    "clippers": "LA Clippers",
    "lac": "LA Clippers",
    "memphis grizzlies": "Memphis Grizzlies",
    "grizzlies": "Memphis Grizzlies",
    "mem": "Memphis Grizzlies",
    "memphis": "Memphis Grizzlies",
    "minnesota timberwolves": "Minnesota Timberwolves",
    "timberwolves": "Minnesota Timberwolves",
    "wolves": "Minnesota Timberwolves",
    "min": "Minnesota Timberwolves",
    "minnesota": "Minnesota Timberwolves",
    "new orleans pelicans": "New Orleans Pelicans",
    "pelicans": "New Orleans Pelicans",
    "nop": "New Orleans Pelicans",
    "new orleans": "New Orleans Pelicans",
    "oklahoma city thunder": "Oklahoma City Thunder",
    "thunder": "Oklahoma City Thunder",
    "okc": "Oklahoma City Thunder",
    "oklahoma city": "Oklahoma City Thunder",
    "phoenix suns": "Phoenix Suns",
    "suns": "Phoenix Suns",
    "phx": "Phoenix Suns",
    "phoenix": "Phoenix Suns",
    "portland trail blazers": "Portland Trail Blazers",
    "trail blazers": "Portland Trail Blazers",
    "blazers": "Portland Trail Blazers",
    "por": "Portland Trail Blazers",
    "portland": "Portland Trail Blazers",
    "sacramento kings": "Sacramento Kings",
    "kings": "Sacramento Kings",
    "sac": "Sacramento Kings",
    "sacramento": "Sacramento Kings",
    "san antonio spurs": "San Antonio Spurs",
    "spurs": "San Antonio Spurs",
    "sas": "San Antonio Spurs",
    "san antonio": "San Antonio Spurs",
    "utah jazz": "Utah Jazz",
    "jazz": "Utah Jazz",
    "uta": "Utah Jazz",
    "utah": "Utah Jazz",
    "los angeles lakers": "Los Angeles Lakers",
    "lakers": "Los Angeles Lakers",
    "lal": "Los Angeles Lakers",
    "la lakers": "Los Angeles Lakers",
}
