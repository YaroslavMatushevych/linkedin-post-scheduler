"""
Main orchestrator — run by GitHub Actions on schedule.
Fetches articles, generates a LinkedIn post, sends to Telegram for review.
"""
import sys

from src.fetcher import get_top_articles
from src.generator import generate_post
from src.state import save_draft
from src.telegram_sender import send_draft


def run() -> None:
    print("Fetching top articles...")
    articles = get_top_articles()

    if not articles:
        print("No relevant articles found today. Skipping.")
        sys.exit(0)

    # Pick the single best article
    article = articles[0]
    print(f"Selected: [{article['source']}] {article['title']} (score={article['score']})")

    print("Generating LinkedIn post with Gemini...")
    post_text = generate_post(article)
    print(f"Generated ({len(post_text)} chars):\n{post_text}\n")

    print("Sending to Telegram...")
    message_id = send_draft(post_text, draft_id="temp", article=article)

    # Save draft with real message_id (need chat_id from config)
    from src.config import TELEGRAM_CHAT_ID
    draft_id = save_draft(post_text, article, message_id, TELEGRAM_CHAT_ID)

    # Telegram doesn't let us update the callback_data after sending,
    # so we send a second silent edit to update the message with correct draft_id.
    # We rebuild the message via editMessageText with the real draft_id.
    from src.telegram_sender import edit_message
    edit_message(TELEGRAM_CHAT_ID, message_id, post_text, draft_id)

    print(f"Done. Draft ID: {draft_id}, Telegram message: {message_id}")


if __name__ == "__main__":
    run()
