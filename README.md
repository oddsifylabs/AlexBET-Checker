# 🏀 AlexBET Checker

A production-ready Telegram bot that checks sports game results and tells you if your bet won.

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

---

## Roadmap

### Phase 1 — Core Stability (Current)
- [x] Async ESPN API client with retries
- [x] Team alias matching (126 aliases)
- [x] Rate limiting
- [x] Structured logging
- [x] Input validation
- [x] Game status detection (final / in-progress / postponed)
- [ ] Add unit tests (pytest)
- [ ] Health check endpoint for Railway
- [ ] Redis-backed rate limiting (multi-instance deployments)

### Phase 2 — Bet Types
- [ ] **Spread checking** — "Lakers -5.5" → win/loss/push
- [ ] **Over/Under** — "Lakers vs Celtics over 220.5"
- [ ] **Parlay calculator** — Check multiple legs at once
- [ ] **Teaser support** — Adjusted spreads for teasers

### Phase 3 — Multi-Sport Expansion
- [ ] **NFL** — Football scores and betting lines
- [ ] **MLB** — Baseball moneyline, run line, totals
- [ ] **NHL** — Hockey puck line and totals
- [ ] **Soccer** — Premier League, La Liga, Champions League
- [ ] **Auto-detect sport** — Infer league from team name

### Phase 4 — Odds & Data Integration
- [ ] **Live odds comparison** — Pull lines from DraftKings, FanDuel, BetMGM
- [ ] **Closing line value (CLV)** — Compare your bet price to closing line
- [ ] **Historical results DB** — SQLite/PostgreSQL for persistent bet tracking
- [ ] **Trends & analytics** — Win rate, ROI, best/worst teams

### Phase 5 — User Features
- [ ] **User bet history** — Save and review past bets
- [ ] **Bet slip parser** — Upload screenshot, OCR extracts bet details
- [ ] **Push notifications** — Alert when your live bet is close to hitting
- [ ] **Group chat mode** — Compete with friends on bet accuracy
- [ ] **Leaderboards** — Public/private group leaderboards

### Phase 6 — Advanced Tools
- [ ] **AI bet analysis** — Suggest bets based on recent trends
- [ ] **Arbitrage scanner** — Find +EV opportunities across sportsbooks
- [ ] **Bankroll tracker** — Log stakes, track profit/loss over time
- [ ] **Export to CSV/Excel** — Download bet history for tax/accounting
- [ ] **Webhook integrations** — Zapier, Make.com for custom workflows

---

## License

MIT — see [LICENSE](LICENSE)

## About

Built by [Oddsify Labs](https://www.oddsifylabs.com)
