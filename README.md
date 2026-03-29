# LinkedIn Post Scheduler

Automatically finds top software engineering content from Hacker News & Dev.to,
generates a LinkedIn post with Gemini AI, sends it to Telegram for review, and
posts to LinkedIn on approval — all for free.

## Architecture

```
GitHub Actions (cron Mon+Thu)
    → Fetch HN / Dev.to
    → Gemini generates post
    → Telegram message with buttons

Vercel webhook (always-on, free)
    → [Post] → LinkedIn API
    → [Edit] → user replies with new text
    → [Regenerate] → Gemini again
    → [Skip] → ignore

Upstash Redis (free)
    → stores draft state + user edit sessions
```

## Setup (one time, ~20 min)

### 1. Clone & create Vercel project

```bash
npm i -g vercel
cd linkedin-post-scheduler
vercel login
vercel          # follow prompts — creates project on vercel.com
```

### 2. Telegram Bot

1. Message [@BotFather](https://t.me/BotFather) → `/newbot` → copy token
2. Message [@userinfobot](https://t.me/userinfobot) → copy your chat ID
3. Set webhook after Vercel deploy (see step 6)

### 3. Google Gemini API key (free)

1. Go to [aistudio.google.com](https://aistudio.google.com)
2. Create API key → copy it

### 4. LinkedIn OAuth token

```bash
pip install -r requirements.txt
python scripts/setup_linkedin.py
```

Follow the printed URL, authorise, copy the two values printed at the end.

> The token lasts ~60 days. Re-run the script when it expires.

### 5. Upstash Redis (free tier)

1. Sign up at [console.upstash.com](https://console.upstash.com)
2. Create a Redis database (free tier)
3. Copy **REST URL** and **REST Token**

### 6. Add all secrets

**GitHub Secrets** (repo → Settings → Secrets → Actions):

| Secret | Value |
|---|---|
| `GEMINI_API_KEY` | from step 3 |
| `TELEGRAM_BOT_TOKEN` | from step 2 |
| `TELEGRAM_CHAT_ID` | from step 2 |
| `LINKEDIN_ACCESS_TOKEN` | from step 4 |
| `LINKEDIN_PERSON_URN` | from step 4 |
| `UPSTASH_REDIS_REST_URL` | from step 5 |
| `UPSTASH_REDIS_REST_TOKEN` | from step 5 |

**Vercel env vars** — add same variables at vercel.com → project → Settings → Environment Variables.

### 7. Register Telegram webhook

After `vercel --prod` gives you a URL (e.g. `https://linkedin-post-scheduler.vercel.app`):

```bash
curl "https://api.telegram.org/bot<TOKEN>/setWebhook?url=https://linkedin-post-scheduler.vercel.app/api/webhook"
```

### 8. Done!

The job runs **Monday and Thursday at 08:00 UTC**.
You can also trigger it manually: GitHub → Actions → "Generate & Send LinkedIn Post" → Run workflow.

## Changing the schedule

Edit `.github/workflows/schedule.yml`:

```yaml
- cron: "0 8 * * 1"   # Monday  08:00 UTC
- cron: "0 8 * * 4"   # Thursday 08:00 UTC
```

Cron reference: [crontab.guru](https://crontab.guru)
