"""
Fetches breaking news from The Hacker News and identifies trending topics.
Designed for hourly checks to catch emerging stories.
"""
import requests
from datetime import datetime, timedelta
from src.config import BREAKING_NEWS_KEYWORDS, BREAKING_NEWS_MIN_SCORE


def _is_breaking_news_relevant(text: str) -> bool:
    """Check if article title matches breaking news keywords."""
    text_lower = text.lower()
    return any(kw in text_lower for kw in BREAKING_NEWS_KEYWORDS)


def fetch_thehackernews_breaking() -> list[dict]:
    """
    Fetch latest posts from The Hacker News (RSS-style via website).
    Focus on emerging/trending stories.
    """
    try:
        # The Hacker News main feed - get latest stories
        response = requests.get(
            "https://feeds.thehackernews.com/feeds/blogs/security.xml",
            timeout=15,
            headers={"User-Agent": "Mozilla/5.0 (Linux; Android 10)"}
        )
        
        # Parse basic XML (simple approach without external libs)
        content = response.text
        stories = []
        
        # Extract title and link pairs using simple string parsing
        import re
        # Find all <item> blocks
        items = re.findall(r'<item>(.*?)</item>', content, re.DOTALL)
        
        for item in items[:20]:  # Check top 20 recent items
            # Extract title
            title_match = re.search(r'<title>(.*?)</title>', item)
            title = title_match.group(1).strip() if title_match else ""
            
            # Extract link
            link_match = re.search(r'<link>(.*?)</link>', item)
            link = link_match.group(1).strip() if link_match else ""
            
            # Extract pub date
            date_match = re.search(r'<pubDate>(.*?)</pubDate>', item)
            pub_date = date_match.group(1).strip() if date_match else ""
            
            if not title or not link:
                continue
                
            # Check if it's recent (published in last 24 hours)
            try:
                import email.utils
                pub_datetime = email.utils.parsedate_to_datetime(pub_date)
                now = datetime.now(pub_datetime.tzinfo) if pub_datetime.tzinfo else datetime.now()
                age_hours = (now - pub_datetime).total_seconds() / 3600
                
                if age_hours > 24:
                    continue
            except:
                pass  # If we can't parse date, include it
            
            if _is_breaking_news_relevant(title):
                stories.append({
                    "title": title,
                    "url": link,
                    "source": "The Hacker News",
                    "category": "Security" if "security" in content.lower() else "Tech News",
                    "score": 100 + (20 - len(stories)),  # Recent = higher score
                    "comments": 0,
                    "is_breaking": True
                })
        
        return stories
        
    except Exception as e:
        print(f"Error fetching The Hacker News: {e}")
        return []


def fetch_hn_breaking_stories() -> list[dict]:
    """Fetch latest HN stories from last hour (more aggressive than regular fetcher)."""
    try:
        ids = requests.get(
            "https://hacker-news.firebaseio.com/v0/topstories.json", 
            timeout=10
        ).json()[:200]  # Look at more stories for breaking news

        stories = []
        now = datetime.now().timestamp()
        
        for story_id in ids[:50]:  # Check top 50
            try:
                item = requests.get(
                    f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json",
                    timeout=5,
                ).json()
                
                if not item or item.get("type") != "story":
                    continue
                
                # Check if posted within last 2 hours for breaking news
                time_posted = item.get("time", 0)
                age_hours = (now - time_posted) / 3600
                
                if age_hours > 2:  # Only within 2 hours
                    continue
                
                score = item.get("score", 0)
                if score < BREAKING_NEWS_MIN_SCORE:
                    continue
                
                title = item.get("title", "")
                if not _is_breaking_news_relevant(title):
                    continue
                
                stories.append({
                    "title": title,
                    "url": item.get("url") or f"https://news.ycombinator.com/item?id={story_id}",
                    "score": score,
                    "comments": item.get("descendants", 0),
                    "source": "Hacker News",
                    "is_breaking": True,
                    "age_hours": age_hours
                })
            except Exception:
                continue
        
        stories.sort(key=lambda s: s["score"] + s["comments"] * 3, reverse=True)
        return stories[:5]
        
    except Exception as e:
        print(f"Error fetching breaking HN stories: {e}")
        return []


def get_breaking_news() -> list[dict]:
    """Get breaking news from all sources, ranked by recency and engagement."""
    hn_breaking = fetch_hn_breaking_stories()
    hackernews_breaking = fetch_thehackernews_breaking()
    
    combined = hn_breaking + hackernews_breaking
    combined.sort(
        key=lambda s: (s.get("score", 0) + s.get("comments", 0) * 2),
        reverse=True
    )
    
    return combined[:3]  # Return top 3 breaking stories
