import os
import re
import requests
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

TEAM_ALIASES = {
    "new york knicks": "ny",
    "knicks": "ny",
}

def parse_message(text):
    date_match = re.search(r"\b(\d{1,2}/\d{1,2}/\d{4})\b", text)
    if not date_match:
        return None, None

    date_str = date_match.group(1)
    team = text.replace(date_str, "").strip().lower()

    return team, date_str

def fetch_game(team_text, date_str):
    date_obj = datetime.strptime(date_str, "%m/%d/%Y")
    espn_date = date_obj.strftime("%Y%m%d")

    url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard?dates={espn_date}"
    res = requests.get(url, timeout=10)
    res.raise_for_status()

    data = res.json()
    events = data.get("events", [])

    for event in events:
        comps = event["competitions"][0]["competitors"]

        teams = []
        for c in comps:
            teams.append({
                "name": c["team"]["displayName"],
                "score": int(c.get("score", 0)),
                "winner": c.get("winner", False),
            })

        for t in teams:
            if team_text in t["name"].lower():
                opponent = teams[0] if teams[1] == t else teams[1]

                return {
                    "team": t["name"],
                    "opponent": opponent["name"],
                    "team_score": t["score"],
                    "opponent_score": opponent["score"],
                    "winner": t["winner"],
                    "total": t["score"] + opponent["score"]
                }

    return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Send a bet like:\n\nNew York Knicks 4/30/2026"
    )

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    team, date = parse_message(text)

    if not team or not date:
        await update.message.reply_text("Format:\nTeam Name MM/DD/YYYY")
        return

    try:
        result = fetch_game(team, date)

        if not result:
            await update.message.reply_text("No game found.")
            return

        bet = "✅ WON" if result["winner"] else "❌ LOST"

        msg = f"""
🏀 Bet Result

{result['team']} vs {result['opponent']}
Date: {date}

Score:
{result['team']}: {result['team_score']}
{result['opponent']}: {result['opponent_score']}

Total: {result['total']}
Moneyline: {bet}
"""

        await update.message.reply_text(msg)

    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

def main():
    if not TOKEN:
        raise Exception("Missing TELEGRAM_BOT_TOKEN")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()