"""Telegram bot handlers with rate limiting and error handling."""

import logging
import time
from collections import defaultdict
from typing import Optional

from telegram import Update
from telegram.ext import ContextTypes

from config import Config
from espn_client import ESPNClient, ESPNError
from parsers import parse_message, validate_date

logger = logging.getLogger(__name__)

# In-memory rate limiter: user_id -> list of timestamps
_rate_limit_store: dict[int, list[float]] = defaultdict(list)


def _is_rate_limited(user_id: int, max_requests: int, window_seconds: float = 60.0) -> bool:
    """Check if a user has exceeded the rate limit."""
    now = time.time()
    requests = _rate_limit_store[user_id]
    # Filter to only requests within the window
    recent = [t for t in requests if now - t < window_seconds]
    _rate_limit_store[user_id] = recent
    return len(recent) >= max_requests


def _format_result(result, date_str: str) -> str:
    """Format a GameResult into a user-friendly message."""
    if not result.completed:
        status = f"⏳ {result.status_detail}"
        if result.clock:
            status += f" — {result.clock}"
        if result.period:
            status += f" (Q{result.period})"
        bet_status = "🟡 Game in progress"
    else:
        status = "✅ Final"
        bet_status = "✅ WON" if result.winner else "❌ LOST"

    msg = (
        f"🏀 Bet Result\n\n"
        f"{result.team} vs {result.opponent}\n"
        f"Date: {date_str}\n"
        f"Status: {status}\n\n"
        f"Score:\n"
        f"{result.team}: {result.team_score}\n"
        f"{result.opponent}: {result.opponent_score}\n\n"
        f"Total: {result.total}\n"
        f"Moneyline: {bet_status}"
    )
    return msg


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    user = update.effective_user
    logger.info("User %s (%s) started the bot", user.id, user.username)

    welcome_text = (
        "👋 Welcome to the Oddsify Bet Result Bot!\n\n"
        "Send me a bet to check the result:\n"
        "• New York Knicks 4/30/2026\n"
        "• Lakers 5/1/2026\n"
        "• GSW 04-30-2026\n\n"
        "I support team names, nicknames, and abbreviations.\n"
        "Currently checking moneyline only."
    )
    await update.message.reply_text(welcome_text)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming text messages."""
    config: Config = context.bot_data.get("config")
    if not config:
        logger.error("Bot configuration missing from context")
        await update.message.reply_text("Internal error. Please try again later.")
        return

    user = update.effective_user
    user_id = user.id
    text = update.message.text

    logger.info("Message from %s (%s): %s", user_id, user.username, text)

    # Rate limiting
    if _is_rate_limited(user_id, config.max_requests_per_minute):
        logger.warning("Rate limit hit for user %s", user_id)
        await update.message.reply_text(
            "⏳ You're sending requests too fast. Please wait a minute."
        )
        return

    # Parse input
    team, date = parse_message(text)
    if not team or not date:
        await update.message.reply_text(
            "❌ I couldn't understand that.\n\n"
            "Format: Team Name MM/DD/YYYY\n"
            "Examples:\n"
            "• New York Knicks 4/30/2026\n"
            "• Lakers 5/1/2026"
        )
        return

    # Validate date
    valid_date = validate_date(date)
    if not valid_date:
        await update.message.reply_text(
            "❌ Invalid date. Please use MM/DD/YYYY format with a real date."
        )
        return

    # Fetch game
    await update.message.chat.send_action(action="typing")

    try:
        async with ESPNClient(timeout=config.espn_timeout) as client:
            result = await client.fetch_game(team, date)
    except ESPNError as e:
        logger.warning("ESPN error for user %s: %s", user_id, e)
        await update.message.reply_text(f"⚠️ {e}")
        return
    except Exception as e:
        logger.exception("Unexpected error fetching game for user %s", user_id)
        await update.message.reply_text(
            "😵 Something went wrong on our end. The team has been notified."
        )
        return

    if not result:
        await update.message.reply_text(
            f"🔍 No game found for {team} on {date}.\n\n"
            "Tips:\n"
            "• Make sure the date is correct\n"
            "• Try the full team name or abbreviation\n"
            "• Games might not be scheduled yet"
        )
        return

    msg = _format_result(result, date)
    await update.message.reply_text(msg)


async def error_handler(update: Optional[Update], context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors caused by updates."""
    logger.error("Update %s caused error: %s", update, context.error, exc_info=context.error)
