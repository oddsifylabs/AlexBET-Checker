"""Telegram bot handlers with rate limiting and error handling."""

import logging
import time
from collections import defaultdict
from typing import Optional

from telegram import Update
from telegram.ext import ContextTypes

from config import Config, BOOKMAKER_NAMES
from espn_client import ESPNClient, ESPNError
from evaluator import evaluate_bet
from odds_client import OddsAPIClient
from parsers import BetRequest, parse_message, validate_date

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


def _format_bet_result(bet_result, date_str: str) -> str:
    """Format a BetResult into a user-friendly message."""
    req = bet_result.bet_request
    game = bet_result.game_result

    # Status emoji
    if not game.completed:
        status = f"⏳ {game.status_detail}"
        if game.clock:
            status += f" — {game.clock}"
        if game.period:
            status += f" (P{game.period})"
    else:
        status = "✅ Final"

    # Outcome emoji
    outcome_emojis = {
        "win": "✅ WON",
        "loss": "❌ LOST",
        "push": "🟡 PUSH",
        "pending": "🟡 PENDING",
    }
    outcome_emoji = outcome_emojis.get(bet_result.outcome, "❓")

    # Sport emoji
    sport_emojis = {
        "nba": "🏀",
        "nfl": "🏈",
        "mlb": "⚾",
        "nhl": "🏒",
        "ncaaf": "🏈",
        "ncaab": "🏀",
    }
    sport_emoji = sport_emojis.get(req.sport, "🏆")

    lines = [
        f"{sport_emoji} Bet Result",
        "",
        f"{game.team} vs {game.opponent}",
        f"Date: {date_str}",
        f"Status: {status}",
        "",
        f"Score:",
        f"{game.team}: {game.team_score}",
        f"{game.opponent}: {game.opponent_score}",
        "",
        f"Bet: {bet_result.bet_type_display} {bet_result.user_line_display}",
        f"Result: {outcome_emoji}",
    ]

    if game.completed:
        lines.append(f"Detail: {bet_result.result_detail}")

        # CLV section
        if bet_result.book_clvs:
            clv_lines = []
            for bc in bet_result.book_clvs:
                if bc.closing_line is not None and bc.clv_display is not None:
                    name = BOOKMAKER_NAMES.get(bc.book_key, bc.book_name)
                    clv_lines.append(
                        f"{name}: {bc.closing_line} ({bc.clv_display})"
                    )

            if clv_lines:
                lines.append("")
                lines.append("📊 CLV by Book:")
                lines.extend(clv_lines)

                if bet_result.avg_clv_display:
                    lines.append(f"Avg CLV: {bet_result.avg_clv_display}")
        elif req.bet_type == "moneyline":
            lines.append("CLV: Moneyline CLV not yet supported")
        else:
            lines.append("CLV: No closing line data available")

    return "\n".join(lines)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    user = update.effective_user
    logger.info("User %s (%s) started the bot", user.id, user.username)

    welcome_text = (
        "👋 Welcome to AlexBET Checker!\n\n"
        "Send me a bet to check the result:\n\n"
        "*Moneyline*\n"
        "• Lakers 5/1/2026\n"
        "• NFL Chiefs 9/10/2026\n\n"
        "*Spread*\n"
        "• Lakers -5.5 5/1/2026\n"
        "• NFL Chiefs -3 9/10/2026\n\n"
        "*Over / Under*\n"
        "• Lakers O 220.5 5/1/2026\n"
        "• NFL Chiefs vs Ravens U 47.5 9/10/2026\n\n"
        "Sports: NBA, NFL, MLB, NHL, NCAAF, NCAAB\n"
        "CLV checked across: DK, FD, MGM, Caesars, PB, Bovada, Barstool, Wynn, Rivers"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")


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
    bet: Optional[BetRequest] = parse_message(text)
    if not bet:
        await update.message.reply_text(
            "❌ I couldn't understand that.\n\n"
            "Format examples:\n"
            "• Team Name MM/DD/YYYY\n"
            "• Lakers -5.5 5/1/2026\n"
            "• Chiefs vs Ravens U 47.5 9/10/2026\n"
            "• NHL Oilers +1.5 5/1/2026"
        )
        return

    # Validate date
    valid_date = validate_date(bet.date)
    if not valid_date:
        await update.message.reply_text(
            "❌ Invalid date. Please use MM/DD/YYYY format with a real date."
        )
        return

    # Fetch game
    await update.message.chat.send_action(action="typing")

    try:
        async with ESPNClient(sport=bet.sport, timeout=config.espn_timeout) as client:
            game = await client.fetch_game(bet.team, bet.date)
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

    if not game:
        await update.message.reply_text(
            f"🔍 No game found for {bet.team} on {bet.date}.\n\n"
            "Tips:\n"
            "• Make sure the date is correct\n"
            "• Try the full team name or abbreviation\n"
            "• Check the sport (default is NBA)\n"
            "• Games might not be scheduled yet"
        )
        return

    # Fetch closing lines for CLV (best effort)
    multi_book_lines = None
    if config.odds_api_key:
        try:
            async with OddsAPIClient(api_key=config.odds_api_key, timeout=config.espn_timeout) as odds_client:
                multi_book_lines = await odds_client.fetch_closing_lines(
                    sport=bet.sport,
                    team=bet.team,
                    opponent=game.opponent,
                    date_str=bet.date,
                )
        except Exception:
            logger.exception("Odds API fetch failed for user %s", user_id)
            # Non-fatal — continue without CLV

    # Evaluate bet
    bet_result = evaluate_bet(bet, game, multi_book_lines)
    msg = _format_bet_result(bet_result, bet.date)
    await update.message.reply_text(msg)


async def error_handler(update: Optional[Update], context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors caused by updates."""
    logger.error("Update %s caused error: %s", update, context.error, exc_info=context.error)
