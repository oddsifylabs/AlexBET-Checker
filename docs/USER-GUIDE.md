# AlexBET User Guide
## Signal Pro + Checker — Complete Setup & Usage

---

## Table of Contents
1. [What Are These Bots?](#what-are-these-bots)
2. [Telegram Group Setup](#telegram-group-setup)
3. [AlexBET Signal Pro Commands](#alexbet-signal-pro-commands)
4. [AlexBET Checker Commands](#alexbet-checker-commands)
5. [Understanding Your Results](#understanding-your-results)
6. [Track Record & Social Proof](#track-record--social-proof)
7. [Troubleshooting](#troubleshooting)

---

## What Are These Bots?

**AlexBET Signal Pro** — Finds +EV (positive expected value) betting opportunities across 6 sports. Scans live odds, detects edges where the market consensus differs from a sportsbook's line, and delivers clean, actionable signals with confidence levels and stake suggestions.

**AlexBET Checker** — Checks your bets against live ESPN scores. Paste any bet in natural language and get instant win/loss/push results plus closing line value (CLV) analysis.

---

## Telegram Group Setup

### Why You Need a Private Group

AlexBET Signal Pro uses a private Telegram group for:
- **Access control** — Only members can use `/scan`, `/signals`, and other premium commands
- **Auto-posted results** — Graded signal results automatically post to the group for social proof
- **Community trust** — Members see real-time win/loss updates as they happen

### Step 1: Create the Private Group

1. In Telegram, tap the **Pencil icon** → **New Group**
2. Name it something like **“AlexBET Inner Circle”** or **“Oddsify Signals”**
3. Add the AlexBET Signal Pro bot to the group
4. Make the bot an **administrator** with these permissions:
   - ✅ Send Messages
   - ✅ Delete Messages
   - ✅ Pin Messages
   - ✅ Manage Invite Links
   - ✅ Restrict Members
5. Set the group to **Private** (not discoverable via search)

### Step 2: Get the Group ID

You need the group’s numeric ID for the bot config:

1. Send any message in the group
2. Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
3. Look for `"chat":{"id":-1001234567890,...}` — that number is your `PRIVATE_GROUP_ID`

> **Note:** Group IDs always start with `-100` followed by digits.

### Step 3: Set the Environment Variable

In your Railway dashboard (or `.env` file):

```env
PRIVATE_GROUP_ID=-1001234567890
```

Redeploy after setting this.

### Step 4: Test Membership Gating

1. Have a non-member DM the bot and type `/scan`
2. They should see:
   > 🔒 This bot is exclusive to group members.
   > Join our private Telegram group to unlock all features: /subscribe
3. Send them `/join` to generate a single-use invite link

### Step 5: Invite Members

**For paying subscribers:**
- Send `/join` in the bot DM → bot generates a single-use, 1-hour invite link
- Send the link to the subscriber

**For bulk invites:**
- In the group, go to **Group Info** → **Add Members**
- Or generate invite links manually with custom expiry

---

## AlexBET Signal Pro Commands

| Command | Who Can Use | What It Does |
|---------|------------|--------------|
| `/start` | Anyone | Welcome message + onboarding |
| `/join` | Anyone | Generate single-use private group invite |
| `/scan` | Members only | Scan live odds for +EV signals |
| `/signals` | Members only | View track record, streaks, recent signals |
| `/upload` | Members only | Upload `.txt` file of bets for AI grading |
| `/analyze` | Members only | AI PLACE/PASS recommendation on uploaded bets |
| `/export_csv` | Members only | Download last scan as CSV |
| `/bankroll` | Members only | Set your betting bankroll (used for stake sizing) |
| `/timezone` | Members only | Set timezone (EST/CST/MST/PST) |
| `/status` | Anyone | Check subscription tier |
| `/subscribe` | Anyone | Upgrade to paid tier via Whop |
| `/help` | Anyone | Show all commands |

### Using `/scan`

1. Type `/scan` in your DM with the bot
2. Bot fetches live odds from The Odds API across NBA, NFL, MLB, NHL, ATP, EPL
3. You receive:
   - **Summary card** — Total signals, avg edge, confidence, breakdown by market
   - **Individual signal cards** — Each signal gets its own clean card:
     - The signal (e.g., `Lakers @ +210`)
     - The game and matchup
     - **Why it’s value** — Short explanation of the edge
     - **Confidence badge** — 🔒 HIGH / ✅ SOLID / ⚡ LEAN / 🎲 LOW
     - Edge %, EV %, suggested stake, game time
4. Signals are automatically saved to your track record

### Understanding Signal Cards

```
🏀 SIGNAL #1 — MONEYLINE
━━━━━━━━━━━━━━━

Lakers @ +210
Lakers vs Celtics

📍 Book: DraftKings
💰 Odds: +210

Why it's value:
Consensus market gives this a 53% chance, but DraftKings
is pricing it like a 50% shot. Expected value is strong at +4.5%.

Confidence: ✅ SOLID (72%)
Edge: +3.2% | EV: +4.5%

💡 Suggested stake: $2
⏰ Tip-off: 05/04/26 @ 07:30 PM
```

### Using `/signals`

Shows your full track record:

```
📊 ALEXBET TRACK RECORD (Last 30 Days)

5W — 2L — 1P
Win Rate: 71.4% | ROI: +38.5%
Pending: 3

🔥 Current Streak: 3 WINS
🏆 Longest Win Streak: 4

By Confidence:
HIGH: 2W/0L (100%)
SOLID: 3W/1L (75%)
LEAN: 0W/1L (0%)

━━━━━━━━━━━━━━━

📅 Recent Signals:

✅ Lakers @ +210
Lakers vs Celtics (NBA)
Edge: +3.2% | Conf: 72% | DraftKings
Result: WIN — Celtics 108 — Lakers 112

❌ Chiefs -3
Chiefs vs Ravens (NFL)
Edge: +2.1% | Conf: 65% | FanDuel
Result: LOSS — Chiefs 20 — Ravens 24
```

### Using `/upload` + `/analyze`

1. Create a `.txt` file with your bets, one per line:
   ```
   Lakers +150 5/1/2026
   Chiefs -3 9/10/2026
   Lakers O 220.5 5/1/2026
   ```
2. Send the file to the bot
3. Type `/analyze`
4. Bot returns AI PLACE/PASS recommendations for each bet

---

## AlexBET Checker Commands

AlexBET Checker is a separate bot. Add it to your personal DMs (not the group).

| Command | What It Does |
|---------|-------------|
| `/start` | Welcome + input examples |
| `/help` | Format help |
| `/sports` | Supported leagues |
| `/format` | Accepted input formats |
| `/clv` | Explain closing line value |

### How to Check a Bet

Just send the bet in natural language. No command needed.

**Moneyline:**
```
Lakers 5/1/2026
NFL Chiefs 9/10/2026
Lakers +150 5/1/2026  (includes CLV)
```

**Spread:**
```
Lakers -5.5 5/1/2026
NFL Chiefs -3 9/10/2026
```

**Over/Under:**
```
Lakers O 220.5 5/1/2026
Chiefs vs Ravens U 47.5 9/10/2026
```

**Result card:**
```
🏀 BET RESULT — NBA MONEYLINE
━━━━━━━━━━━━━━━

Lakers +150 vs Celtics
Date: 5/1/2026

Result: ✅ WON
Final: Lakers 112 — Celtics 108

Detail: Lakers won outright

📊 CLV by Book:
DK: +130 (+3.5% ✓)
Avg CLV: +3.5% ✓
```

---

## Track Record & Social Proof

### Auto-Posted Results

Every 3 hours, Signal Pro checks ESPN for finished games and auto-grades pending signals. When a signal is graded:

- **Wins** → Posted to the private group with ✅ emoji
- **Losses** → Posted with ❌ emoji
- **Pushes** → Posted with 🟡 emoji

This builds trust automatically. Members see real results in real time.

### Manual Social Proof

Once you have 5+ graded signals:

1. Run `/signals` in your DM
2. Screenshot the track record
3. Post it to your public channels (X, Telegram channel, etc.)
4. Pin it in your private group

### Best Practices

- **Never delete loss posts.** Transparency builds more trust than a fake 100% record.
- **Highlight streaks.** “3 wins in a row” is more compelling than individual results.
- **Show confidence breakdown.** “HIGH confidence signals: 100% win rate” sells better than raw numbers.

---

## Troubleshooting

### Bot says “You are not a member”

- Make sure you joined the private group
- The bot checks membership on every protected command
- Use `/join` to get a new invite link

### `/scan` returns no signals

- No live games may be scheduled (common late night / early morning)
- Your subscription tier may limit markets (Free = Moneyline only)
- Try again in a few hours when games are closer to tip-off

### Results not posting to group

- Verify `PRIVATE_GROUP_ID` is set correctly in environment variables
- Make sure the bot is an admin in the group
- Check that the group is not muted for the bot

### CLV shows “No data”

- Free Odds API tier only provides current odds, not true historical closing lines
- Add your own odds when placing the bet (e.g., `Lakers +150`) for CLV calculation
- The bot caches odds over time, so CLV improves as the database grows

### Bot is slow or timing out

- `/scan` hits The Odds API 18 times (6 sports × 3 markets)
- Each request has a 5-second timeout
- If APIs are slow, try again in 30 seconds

---

## Quick Reference Card

**Signal Pro (in bot DM):**
```
/start     — Onboarding
/join      — Get group invite
/scan      — Find +EV signals
/signals   — Track record & streaks
/upload    — Upload .txt for AI grading
/analyze   — AI PLACE/PASS
/export_csv — Download CSV
/bankroll  — Set bankroll
/timezone  — Set timezone
```

**Checker (in bot DM, no commands needed):**
```
Lakers +150 5/1/2026          → Check moneyline
Lakers -5.5 5/1/2026          → Check spread
Lakers O 220.5 5/1/2026       → Check total
NFL Chiefs -3 9/10/2026       → Check NFL spread
```

---

*Last updated: May 2026*
