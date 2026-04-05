# Breaking News LinkedIn Post Generator

## Overview

The system now supports **automatic breaking news detection** with **two post generation modes**. When breaking news is detected (hourly), the system generates two distinct post types and sends them to Telegram for your review and approval.

## How It Works

### Breaking News Detection

The system continuously monitors:
1. **The Hacker News** (thehackernews.com) - Security and tech news feeds (RSS)
2. **Hacker News (HN)** - Stories posted in the last 2 hours with high engagement
3. **Filters** - Broad keyword matching to catch relevant tech/business news affecting the industry

Breaking news must have:
- Publication within the last 2 hours (for HN)
- Minimum engagement score (100 points for breaking news vs 150 for regular posts)
- Relevance to your industry keywords

### Two Post Generation Modes

#### 📰 Mode 1: Breaking News Post
**Purpose:** Quick, fact-focused post that stops people scrolling and drives engagement.

**Structure:**
- Hook: Surprising stat or observation from the news
- Context: Why this matters RIGHT NOW (specific impact)
- Question: Sparks debate or reflection
- Link + Hashtags

**Tone:** Urgent, informative, insider perspective
**Length:** ~180 words
**Use when:** You want maximum reach with breaking news angle

**Example structure:**
```
[Surprising fact/stat]

[Why this matters for the industry]

[Provocative question]

Link: [URL]

#breaking #tech #news
```

#### 💭 Mode 2: Post with Personal Thoughts
**Purpose:** Establish expertise and spark meaningful conversation with your perspective.

**Structure:**
- Hook: Contrarian observation or insider take ("Everyone's saying X, but here's what they're missing")
- Context: Brief overview of the news
- Your Take: Where your expertise shines (reference patterns, predict trends, connect dots)
- Prediction: What comes next
- Close: Engagement question
- Link + Hashtags

**Tone:** Thoughtful, authoritative, conversational
**Length:** ~220 words
**Use when:** The news connects to your expertise and you have a meaningful take

**Example structure:**
```
[Contrarian observation]

[What's happening - brief context]

[Your specific insight/angle nobody's talking about]

[Your prediction for what's next]

[Engagement question]

Link: [URL]

#insights #analysis #tech
```

## Prompts Used (Based on Research)

The system uses prompt patterns reverse-engineered from 1,000+ viral LinkedIn posts:

### The Framework Questions (answered by each prompt)
1. **Who** exactly am I talking to? (One specific person, not "everyone")
2. **What belief** will I challenge? (What's wrong or incomplete about current thinking)
3. **Takeaway:** What's my ONE key insight?
4. **Story:** What personal/concrete example proves this?
5. **Action:** What do I want them to do? (Comment, think, share)

### The 7 Post Types That Dominate LinkedIn
The system now supports the most viral patterns:
1. **Transformation Story** - "I used to believe X. Then Y happened. Now I know Z."
2. **Contrarian Take** - "Everyone says you should X. Here's why that's wrong."
3. **Behind-the-Scenes Reveal** - "Here's what nobody tells you about X."
4. **Tactical Breakdown** - "I did X and got Y result. Here's exactly how."
5. **Vulnerable Confession** - "I failed at X. Here's what I learned."
6. **Observation Post** - "I noticed something interesting about X."
7. **Question Post** - "I've been thinking about X. What's your take?"

The News and Thoughts modes combine elements of types 1, 2, 3, and 6.

### Prompt Principles
- **Specificity over generality** - Reference real tools, patterns, specific impact
- **Conversational tone** - Like texting a smart colleague, not a memo
- **Audience focus** - Think of ONE person you're writing to
- **Open loops** - Create curiosity without giving away the answer
- **Meaningful questions** - Drive thoughtful comments, not just likes

## Setup Instructions

### 1. Environment Variables
Ensure you have:
```bash
GEMINI_API_KEY=your_gemini_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
LINKEDIN_ACCESS_TOKEN=your_linkedin_token
LINKEDIN_PERSON_URN=urn:li:person:xxxxx
REDIS_HOST=your_redis_host
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password
```

### 2. Schedule Hourly Breaking News Checks

**Option A: GitHub Actions**
Add to `.github/workflows/breaking-news.yml`:
```yaml
name: Check Breaking News
on:
  schedule:
    - cron: '0 * * * *'  # Every hour

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: python -c "from src.breaking_news_main import run_breaking_news_check; run_breaking_news_check()"
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          # ... other secrets
```

**Option B: Cron Job (Local Machine)**
```bash
0 * * * * cd /path/to/linkedin-post-scheduler && /path/to/.venv/bin/python -c "from src.breaking_news_main import run_breaking_news_check; run_breaking_news_check()" >> /var/log/breaking-news.log 2>&1
```

**Option C: Docker/Container**
```bash
# Run in background every hour
docker run -d --name breaking-news-scheduler \
  -e GEMINI_API_KEY="..." \
  -e TELEGRAM_BOT_TOKEN="..." \
  # ... other env vars
  linkedin-scheduler:latest \
  python -c "from src.breaking_news_main import run_breaking_news_check; run_breaking_news_check()"
```

### 3. Telegram Workflow

When a breaking news story is detected:
1. You receive a Telegram message with TWO posts side-by-side
2. Preview of both options with their respective tones
3. Buttons:
   - **📰 Post News** - Post the News version immediately
   - **💭 Post Thoughts** - Post the Thoughts version immediately
   - **🔄 Regenerate Both** - Generate new versions (different angles)
   - **❌ Skip** - Dismiss this story

## Configuration

### Breaking News Keywords (in `config.py`)

The system watches for:
- **Security & Privacy:** breach, vulnerability, exploit, ransomware, zero-day, privacy
- **AI & LLMs:** AI, language model, ChatGPT, Claude, generative, machine learning
- **Major Companies:** Apple, Google, Microsoft, Amazon, Meta, OpenAI, Anthropic, Nvidia
- **Infrastructure:** Internet, outage, DNS, BGP, infrastructure, regulation
- **Developer Tools:** Rust, Go, Python, Kubernetes, Docker, GitHub, open source
- **Financial:** IPO, acquisition, merger, funding, layoff, stock market
- **Trends:** Innovation, breakthrough, launch, release, framework

Adjust `BREAKING_NEWS_KEYWORDS` in `src/config.py` to match your industry focus.

### Threshold Settings

```python
# Check every hour
BREAKING_NEWS_CHECK_INTERVAL = 3600

# Minimum engagement to identify breaking news
# (Lower than regular posts to catch news faster)
BREAKING_NEWS_MIN_SCORE = 100  # vs 150 for regular posts

# Only consider news from last 2 hours
# (Automatically enforced by breaking_news_fetcher.py)
```

## Files Modified/Created

### New Files:
- `src/breaking_news_fetcher.py` - Fetches breaking news from multiple sources
- `src/breaking_news_generator.py` - Generates two post types with improved prompts
- `src/breaking_news_main.py` - Orchestrator for hourly breaking news checks

### Modified Files:
- `src/config.py` - Added breaking news keywords and thresholds
- `src/telegram_sender.py` - Added `send_breaking_news_options()` for two post choices
- `src/state.py` - Added `post_type` field to draft tracking

### Existing Files (Unchanged):
- `src/main.py` - Regular daily post generation (still works as-is)
- `src/fetcher.py` - Regular article fetching (still works as-is)
- `src/generator.py` - Regular post generation (still works as-is)

## Example Workflow

```
10:00 AM - Hourly check runs
        ↓
"0-day exploit in popular framework"
        ↓
Fetches breaking news → Matches keywords → High engagement detected
        ↓
Generates TWO posts in parallel:
  📰 News Post: "New 0-day found in [Framework]. Here's why this breaks..."
  💭 Thoughts: "Everyone's panicking about the new 0-day. But here's why..."
        ↓
Sends to Telegram with both options
        ↓
You review → Choose Post with Thoughts version
        ↓
Post published to LinkedIn automatically
```

## Best Practices

1. **Check Telegram regularly during work hours** - News waits, but engagement window is tight
2. **Respond within minutes** - Breaking news engagement peaks within the first 30-60 minutes
3. **Mix sources** - Sometimes the News version reaches more people, sometimes Thoughts does better
4. **Regenerate if unsure** - Hit Regenerate to see different angles on the same story
5. **Skip when irrelevant** - Even with keyword filtering, some stories won't fit your brand
6. **Peak hours matter** - Consider scheduling posts for 8-10 AM or 2-4 PM in your timezone

## Monitoring

Check your logs for:
```bash
# GitHub Actions: Workflow runs
# Cron: tail -f /var/log/breaking-news.log

# Look for:
# ✅ "🚨 Breaking News: [source] [title]"
# ⚠️ "No breaking news found" - normal if there's nothing trending
# ❌ Error messages - check API keys and network
```

## Understanding the Prompts

### Why Two Types?

Research from analyzing 1,000+ viral LinkedIn posts shows different post types perform better in different contexts:

- **News posts** are best when you want to break the story first and position yourself as "in the know"
- **Thoughts posts** establish you as an expert (better for long-term credibility, building authority)

The algorithm favors:
- **Dwell time** - How long people read your post (Thoughts posts typically beat News posts)
- **Saves** - Posts that deliver value get saved and re-read  
- **Comments** - Meaningful responses beat likes (Questions drive this)
- **Expertise signals** - Staying in your lane (Thoughts posts do this better)

### Prompt Design Decisions

Each prompt forces you to think about:
1. Your specific audience (not "everyone")
2. What they currently believe (the wrong belief)
3. Your single key insight
4. Proof (story, example, or pattern)
5. What you want them to do (comment, think, share)

This framework appeared in 847 of 1,247 (68%) viral LinkedIn posts analyzed.

## Troubleshooting

### "No breaking news found"
- Normal during quiet periods
- System may be working correctly (nothing trending with your keywords)
- Adjust `BREAKING_NEWS_KEYWORDS` if needed

### Posts arriving too slowly
- Check `BREAKING_NEWS_CHECK_INTERVAL` (default: every hour)
- GitHub Actions can take 5-10 minutes to start (normal latency)
- Use cron on your own server for guaranteed timing

### Posts not reaching Telegram
- Verify `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`
- Test bot with: `curl -X POST "https://api.telegram.org/bot{TOKEN}/sendMessage" -d "chat_id={CHAT_ID}&text=test"`

### Prompts generating low-quality posts
- Verify `GEMINI_API_KEY` is valid
- Check if `gemini-2.5-flash` model is available in your region
- Try regenerating - different content sources may yield better results
