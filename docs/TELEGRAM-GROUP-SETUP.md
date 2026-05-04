# AlexBET Telegram Group Setup Guide

Complete walkthrough for configuring private group membership, invite links, and auto-posting results.

---

## Overview

AlexBET Signal Pro uses a **private Telegram group** as the gatekeeper:
- Non-members can use `/start`, `/join`, `/status`, `/help`, `/subscribe`
- Members unlock `/scan`, `/signals`, `/upload`, `/analyze`, `/export`, etc.
- Graded results auto-post to the group for social proof

---

## Step 1: Create the Private Group

1. Open Telegram → tap **Pencil icon** → **New Group**
2. Name it (examples):
   - `AlexBET Inner Circle`
   - `Oddsify Signals`
   - `+EV Lab`
3. **Do NOT add members yet**
4. Tap the group name → **Edit** → **Group Type** → set to **Private**

---

## Step 2: Add the Bot as Admin

1. In the group, tap the group name → **Administrators** → **Add Admin**
2. Search for your bot (@AlexBETSignalProBot or whatever your handle is)
3. Enable these permissions:

| Permission | Why Needed |
|------------|-----------|
| ✅ Send Messages | Post result updates |
| ✅ Delete Messages | Clean up spam if needed |
| ✅ Pin Messages | Pin rules or win boards |
| ✅ Manage Invite Links | Generate single-use links via `/join` |
| ✅ Restrict Members | Timeout/ban if needed |
| ✅ Add New Admins | (Optional) if you want co-admins |

4. Tap **Save**

---

## Step 3: Get the Group ID

The bot needs the numeric group ID to check membership.

### Method A: Via BotFather
1. Message [@userinfobot](https://t.me/userinfobot) on Telegram
2. Forward any message from your group to the bot
3. It replies with the group ID (format: `-1001234567890`)

### Method B: Via API
1. Send any message in the group
2. Visit this URL in your browser:
   ```
   https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
   ```
3. Search the JSON for `"chat":{"id":-1001234567890`
4. Copy that number — that’s your `PRIVATE_GROUP_ID`

> **Important:** Group IDs always start with `-100`.

---

## Step 4: Configure Environment

### Railway Dashboard
1. Go to [railway.app](https://railway.app) → your Signal Pro service
2. Click **Variables** → **New Variable**
3. Name: `PRIVATE_GROUP_ID`
4. Value: `-1001234567890` (your actual ID)
5. Click **Add**
6. Railway redeploys automatically

### Or in `.env` file (local dev)
```env
PRIVATE_GROUP_ID=-1001234567890
TELEGRAM_BOT_TOKEN=your_token_here
ODDS_API_KEY=your_key_here
```

---

## Step 5: Test Everything

### Test 1: Non-member gets blocked
1. Ask someone who is NOT in the group to DM the bot
2. They type `/scan`
3. Should see:
   ```
   🔒 This bot is exclusive to group members.

   Join our private Telegram group to unlock all features:
   /subscribe for access details.
   ```

### Test 2: Member passes through
1. Add yourself to the group
2. DM the bot `/scan`
3. Should scan odds normally

### Test 3: `/join` generates invite
1. Have a non-member DM the bot `/join`
2. Bot should reply with a single-use invite link
3. Link expires in 1 hour and can only be used once

### Test 4: Auto-post results
1. Run `/scan` so signals get saved
2. Wait for a game to finish (or wait for the next 3-hour auto-grade cycle)
3. Check the group — graded results should appear automatically

---

## Step 6: Group Rules & Pinning

Pin these rules in the group for clarity:

```
🎯 AlexBET Inner Circle Rules

✅ This bot finds +EV signals across NBA, NFL, MLB, NHL, ATP, EPL
✅ Run /scan for live signals
✅ Run /signals to see our track record
✅ All results auto-post here — wins AND losses
✅ Never DM the bot /scan from inside this group — DM the bot directly

🔒 Do NOT share invite links. Each link is single-use.
🛑 Violations = instant removal, no refund.
```

To pin:
1. Send the rules message
2. Long-press → **Pin**
3. Choose **Pin for all members**

---

## Invite Link Strategy

| Scenario | How to Invite |
|----------|--------------|
| Single subscriber | Tell them to DM bot `/join` → bot sends single-use link |
| Bulk add (you know them) | Add directly in group settings |
| Public promotion | Create a separate public channel that funnels to /join |

### Revoking Compromised Links
If an invite link leaks:
1. Go to **Group Info** → **Invite Links**
2. Tap **Revoke** on the leaked link
3. All existing members stay — only the link dies

---

## FAQ

**Q: Can I use the bot without a private group?**
A: Yes — leave `PRIVATE_GROUP_ID` empty. All commands will be open to everyone. Not recommended for paid products.

**Q: What if the bot leaves the group?**
A: Add it back and re-promote to admin. Membership checks will fail until the bot rejoins.

**Q: Can I have multiple private groups?**
A: Not with the current setup. One `PRIVATE_GROUP_ID` per bot instance.

**Q: Do members need to stay in the group to keep access?**
A: Yes. If someone leaves, `/scan` will block them on the next command. They’d need `/join` again.

**Q: What happens if I change the group from private to public?**
A: The bot still works, but anyone can find and join the group via search. Keep it private.

---

*Last updated: May 2026*
