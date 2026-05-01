# 🏀 Oddsify Bet Result Bot

A production-ready Telegram bot that checks NBA game results and tells you if your moneyline bet won.

## Features

- **Moneyline Results** — Instantly check if your team won or lost
- **Smart Team Matching** — Supports full names, nicknames, city names, and abbreviations (e.g. `Lakers`, `LA`, `LAL`, `Los Angeles Lakers`)
- **Live Game Status** — Know if the game is final, in progress, or postponed
- **Rate Limiting** — Prevents abuse and protects the ESPN API
- **Robust Error Handling** — Friendly messages when ESPN is down or the game isn't found
- **Async Architecture** — Built with `httpx` and `python-telegram-bot` v21 for high performance
- **Retry Logic** — Automatic retries with exponential backoff on transient ESPN failures
- **Modular Codebase** — Clean separation of concerns for easy maintenance

## Supported Input Formats

```
New York Knicks 4/30/2026
Lakers 5/1/2026
GSW 04-30-2026
nyk 4/30/2026
Golden State 2026-04-30
```

## Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/oddsifylabs/telegram-bet-bot.git
cd telegram-bet-bot
```

### 2. Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env and set your TELEGRAM_BOT_TOKEN
```

### 4. Run locally

```bash
python bot.py
```

## Deploy (Railway)

1. Push this repo to GitHub
2. Create a new project on [Railway](https://railway.app)
3. Connect your GitHub repo
4. Add environment variable:
   - `TELEGRAM_BOT_TOKEN` — from [@BotFather](https://t.me/BotFather)
5. Deploy!

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `TELEGRAM_BOT_TOKEN` | Yes | — | Bot token from @BotFather |
| `ESPN_TIMEOUT` | No | `10` | ESPN API request timeout (seconds) |
| `MAX_REQUESTS_PER_MINUTE` | No | `10` | Per-user rate limit |
| `LOG_LEVEL` | No | `INFO` | Logging verbosity: DEBUG, INFO, WARNING, ERROR |

## Architecture

```
telegram-bet-bot/
├── bot.py          # Entry point — sets up logging and polling
├── config.py       # Environment config, constants, team aliases
├── parsers.py      # Message parsing, validation, team normalization
├── espn_client.py  # Async ESPN API client with retries
├── handlers.py     # Telegram command/message handlers + rate limiting
├── requirements.txt
├── Procfile
├── runtime.txt
├── .env.example
├── .gitignore
└── README.md
```

## Known Limitations

- **Moneyline only** — Spread and over/under are not yet supported
- **NBA only** — Other leagues are not yet supported
- **Date boundaries** — ESPN uses UTC-relative date ranges. A very late-night game may appear under the next calendar day
- **In-progress games** — Results shown as "in progress"; final status updates when the game ends

## Roadmap

- [ ] Spread & over/under support
- [ ] Additional leagues (NFL, MLB, NHL, soccer)
- [ ] Persistent user bet history
- [ ] Odds comparison integration
- [ ] Parlay calculator
- [ ] Redis-backed rate limiting for multi-instance deployments

## License

MIT — see [LICENSE](LICENSE)

## About

Built by [Oddsify Labs](https://www.oddsifylabs.com)
