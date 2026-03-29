"""
Fetches top articles from Hacker News and Dev.to,
filtered for topics relevant to a senior software engineer.
"""
import requests
from src.config import HN_CANDIDATE_POOL, HN_MIN_SCORE, RELEVANT_KEYWORDS


def _is_relevant(text: str) -> bool:
    text_lower = text.lower()
    return any(kw in text_lower for kw in RELEVANT_KEYWORDS)


def fetch_hn_best() -> list[dict]:
    """Fetch top HN stories, return those that are relevant."""
    ids = requests.get(
        "https://hacker-news.firebaseio.com/v0/beststories.json", timeout=10
    ).json()[:HN_CANDIDATE_POOL]

    stories = []
    for story_id in ids:
        try:
            item = requests.get(
                f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json",
                timeout=5,
            ).json()
            if not item or item.get("type") != "story":
                continue
            if item.get("score", 0) < HN_MIN_SCORE:
                continue
            title = item.get("title", "")
            if not _is_relevant(title):
                continue
            stories.append(
                {
                    "title": title,
                    "url": item.get("url") or f"https://news.ycombinator.com/item?id={story_id}",
                    "score": item.get("score", 0),
                    "comments": item.get("descendants", 0),
                    "source": "Hacker News",
                }
            )
        except Exception:
            continue

    # Sort by engagement (score + comments weight)
    stories.sort(key=lambda s: s["score"] + s["comments"] * 2, reverse=True)
    return stories[:10]


def fetch_devto_articles() -> list[dict]:
    """Fetch top weekly Dev.to articles relevant to SE."""
    try:
        resp = requests.get(
            "https://dev.to/api/articles?top=7&per_page=20",
            timeout=10,
        )
        articles = resp.json()
    except Exception:
        return []

    results = []
    for a in articles:
        title = a.get("title", "")
        if not _is_relevant(title):
            continue
        results.append(
            {
                "title": title,
                "url": a.get("url", ""),
                "score": a.get("public_reactions_count", 0),
                "comments": a.get("comments_count", 0),
                "source": "Dev.to",
            }
        )
    results.sort(key=lambda s: s["score"] + s["comments"], reverse=True)
    return results[:5]


def get_top_articles() -> list[dict]:
    """Merge and rank articles from all sources, return top 5."""
    hn = fetch_hn_best()
    devto = fetch_devto_articles()
    combined = hn + devto
    combined.sort(key=lambda s: s["score"] + s["comments"] * 2, reverse=True)
    return combined[:5]
