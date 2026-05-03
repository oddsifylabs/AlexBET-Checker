# 🏆 AlexBET Checker

A production-ready Telegram bot that checks sports game results and tells you if your bet won — now with **spread**, **over/under**, **multi-sport support**, and **Closing Line Value (CLV)**.

## Features

- **Moneyline ✓** — Instantly check if your team won or lost
- **Spread ✓** — "Lakers -5.5" → win/loss/push with margin
- **Over/Under ✓** — "Lakers O 220.5" → evaluated against final total
- **Multi-Sport ✓** — NBA, NFL, MLB, NHL, NCAAF, NCAAB
- **CLV Check ✓** — Compare your line to the market closing line (requires Odds API key)
- **Smart Team Matching** — Full names, nicknames, city names, and abbreviations across all supported leagues
- **Live Game Status** — Know if the game is final, in progress, or postponed
- **Rate Limiting** — Prevents abuse and protects APIs
- **Robust Error Handling** — Friendly messages when ESPN or odds APIs are down
- **Async Architecture** — Built with `httpx` and `python-telegram-bot` v21 for high performance
- **Retry Logic** — Automatic retries with exponential backoff on transient failures
- **Modular Codebase** — Clean separation of concerns for easy maintenance

## Supported Input Formats

### Moneyline
```
Lakers 5/1/2026
NFL Chiefs 9/10/2026
NHL Oilers 5/1/2026
```

### Spread
```
Lakers -5.5 5/1/2026
NFL Chiefs -3 9/10/2026
MLB Yankees +1.5 5/1/2026
```

### Over / Under
```
Lakers O 220.5 5/1/2026
NFL Chiefs vs Ravens U 47.5 9/10/2026
NHL Oilers vs Canucks O 6.5 5/1/2026
```

### Sport Prefix
```
NBA Lakers -5.5 5/1/2026
NFL Chiefs 9/10/2026
MLB Yankees 5/1/2026
NHL Oilers 5/1/2026
NCAAF Alabama 9/5/2026
NCAAB Duke 3/20/2026
```

## Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/oddsifylabs/AlexBET-Checker.git
cd AlexBET-Checker
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
# Optional: set ODDS_API_KEY for CLV checks
```

### 4. Run locally

```bash
python bot.py
```

## Deploy (Railway)

1. Push this repo to GitHub
2. Create a new project on [Railway](https://railway.app)
3. Connect your GitHub repo
4. Add environment variables:
   - `TELEGRAM_BOT_TOKEN` — from [@BotFather](https://t.me/BotFather)
   - `ODDS_API_KEY` — optional, from [The Odds API](https://the-odds-api.com/)
5. Deploy!

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `TELEGRAM_BOT_TOKEN` | Yes | — | Bot token from @BotFather |
| `ODDS_API_KEY` | No | — | API key for closing line value checks |
| `ESPN_TIMEOUT` | No | `10` | ESPN API request timeout (seconds) |
| `MAX_REQUESTS_PER_MINUTE` | No | `10` | Per-user rate limit |
| `LOG_LEVEL` | No | `INFO` | Logging verbosity: DEBUG, INFO, WARNING, ERROR |

## Architecture

```
AlexBET-Checker/
├── bot.py              # Entry point — sets up logging and polling
├── config.py           # Environment config, constants, team aliases
├── parsers.py          # Message parsing, bet type detection, team normalization
├── espn_client.py      # Async ESPN API client with retries (multi-sport)
├── odds_client.py      # The Odds API client for CLV lookups
├── evaluator.py        # Bet evaluation logic (ML, spread, total, push, CLV)
├── handlers.py         # Telegram command/message handlers + rate limiting
├── requirements.txt
├── Procfile
├── runtime.txt
├── .env.example
├── .gitignore
└── README.md
```

## Supported Sports

| Sport | ESPN Key | Team Aliases | Notes |
|-------|----------|--------------|-------|
| NBA | `basketball/nba` | 30 teams | Default if no sport specified |
| NFL | `football/nfl` | 32 teams | Spread and totals supported |
| MLB | `baseball/mlb` | 30 teams | Run line + totals |
| NHL | `hockey/nhl` | 32 teams | Puck line + totals |
| NCAAF | `football/college-football` | Top teams | Major programs |
| NCAAB | `basketball/mens-college-basketball` | Top teams | Major programs |

## How CLV Works

**Closing Line Value (CLV)** measures whether you beat the market.

- **Spread**: If you took `-5.5` and the game closed `-7`, your CLV is negative (you got a worse line than the sharps).
- **Total**: If you took `Over 220.5` and the game closed `O 222`, your CLV is negative.
- **Positive CLV** over time is a strong indicator of +EV betting.

CLV requires a free [The Odds API](https://the-odds-api.com/) key. Without a key, the bot evaluates your bet but skips the CLV comparison.

## Known Limitations

- **Date boundaries** — ESPN uses UTC-relative date ranges. A very late-night game may appear under the next calendar day
- **In-progress games** — Results shown as "in progress"; final status updates when the game ends
- **CLV data** — The Odds API free tier provides current/upcoming odds. True historical closing lines may require a premium plan
- **College teams** — Only major NCAA programs are aliased; obscure teams may not match

---

## Roadmap

### Phase 1 — Core Stability (Completed)
- [x] Async ESPN API client with retries
- [x] Team alias matching (200+ aliases across 6 sports)
- [x] Rate limiting
- [x] Structured logging
- [x] Input validation
- [x] Game status detection (final / in-progress / postponed)

### Phase 2 — Bet Types (Completed)
- [x] **Spread checking** — "Lakers -5.5" → win/loss/push
- [x] **Over/Under** — "Lakers vs Celtics over 220.5"
- [x] **Push handling** — Correctly identifies and labels pushes
- [ ] **Parlay calculator** — Check multiple legs at once
- [ ] **Teaser support** — Adjusted spreads for teasers

### Phase 3 — Multi-Sport Expansion (Completed)
- [x] **NBA** — Basketball scores and betting lines
- [x] **NFL** — Football scores and betting lines
- [x] **MLB** — Baseball moneyline, run line, totals
- [x] **NHL** — Hockey puck line and totals
- [x] **NCAAF / NCAAB** — Major college programs
- [x] **Auto-detect sport** — Infer league from team name or explicit prefix

### Phase 4 — Odds & Data Integration (In Progress)
- [x] **Closing line value (CLV)** — Compare your bet price to closing line
- [ ] **Live odds comparison** — Pull lines from multiple sportsbooks
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
