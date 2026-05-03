"""AlexBET Checker — Telegram entry point."""

import logging
import sys

from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

from config import Config
from handlers import (
    BOT_COMMANDS,
    clv_command,
    error_handler,
    format_command,
    handle_message,
    help_command,
    sports_command,
    start,
)


def setup_logging(level: str = "INFO") -> None:
    """Configure structured logging for the bot."""
    fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format=fmt,
        stream=sys.stdout,
    )
    # Reduce noise from external libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("telegram").setLevel(logging.WARNING)


async def _post_init(app) -> None:
    """Set bot commands menu after startup."""
    await app.bot.set_my_commands(BOT_COMMANDS)


def main() -> None:
    """Run the bot."""
    config = Config.from_env()
    setup_logging(config.log_level)

    logger = logging.getLogger(__name__)
    logger.info("Starting AlexBET Checker")
    logger.info("Log level: %s", config.log_level)

    app = (
        ApplicationBuilder()
        .token(config.telegram_token)
        .post_init(_post_init)
        .build()
    )

    # Store config for handler access
    app.bot_data["config"] = config

    # Register handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("sports", sports_command))
    app.add_handler(CommandHandler("format", format_command))
    app.add_handler(CommandHandler("clv", clv_command))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )
    app.add_error_handler(error_handler)

    logger.info("Bot polling started")
    app.run_polling()


if __name__ == "__main__":
    main()
