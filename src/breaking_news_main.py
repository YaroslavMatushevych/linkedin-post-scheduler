"""
Breaking news orchestrator — checks for trending news hourly.
Generates two post options and sends to Telegram for review.
"""
import sys
from src.breaking_news_fetcher import get_breaking_news
from src.breaking_news_generator import generate_breaking_news_post
from src.state import save_draft
from src.telegram_sender import send_breaking_news_options
from src.config import TELEGRAM_CHAT_ID


def run_breaking_news_check() -> None:
    """Check for breaking news and send to Telegram with two post options."""
    print("🔍 Checking for breaking news...")
    news_stories = get_breaking_news()

    if not news_stories:
        print("No breaking news found. Skipping.")
        sys.exit(0)

    # Pick the hottest story
    article = news_stories[0]
    print(f"🚨 Breaking News: [{article['source']}] {article['title']}")
    print(f"   Engagement: {article.get('score', 0)} points, {article.get('comments', 0)} comments")

    # Generate BOTH post types
    print("📰 Generating News Post...")
    post_news = generate_breaking_news_post(article, post_type="news")
    print(f"   Generated ({len(post_news)} chars)")

    print("💭 Generating Post with Thoughts...")
    post_thoughts = generate_breaking_news_post(article, post_type="thoughts")
    print(f"   Generated ({len(post_thoughts)} chars)")

    # Send both options to Telegram
    print("📤 Sending to Telegram with options...")
    message_id = send_breaking_news_options(article, post_news, post_thoughts)
    
    # Save drafts for later reference
    draft_id_news = save_draft(post_news, article, message_id, TELEGRAM_CHAT_ID, post_type="news")
    draft_id_thoughts = save_draft(post_thoughts, article, message_id, TELEGRAM_CHAT_ID, post_type="thoughts")

    print(f"✅ Done!")
    print(f"   Message ID: {message_id}")
    print(f"   News Draft ID: {draft_id_news}")
    print(f"   Thoughts Draft ID: {draft_id_thoughts}")


if __name__ == "__main__":
    run_breaking_news_check()
