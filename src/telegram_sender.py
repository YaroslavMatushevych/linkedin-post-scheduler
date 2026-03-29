"""
Sends draft posts to Telegram with inline action buttons.
"""
import requests
from src.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


def _api(method: str, payload: dict) -> dict:
    resp = requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/{method}",
        json=payload,
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()


def send_draft(post_text: str, draft_id: str, article: dict) -> int:
    """Send the draft post to Telegram. Returns the message_id."""
    preview = post_text[:800] + ("…" if len(post_text) > 800 else "")
    source_line = f"\n\n🔗 Source: [{article['title']}]({article['url']})"

    message = (
        f"📝 *New LinkedIn draft ready*\n\n"
        f"{preview}"
        f"{source_line}"
    )

    keyboard = {
        "inline_keyboard": [
            [
                {"text": "🚀 Post to LinkedIn", "callback_data": f"post:{draft_id}"},
                {"text": "✏️ Edit", "callback_data": f"edit:{draft_id}"},
            ],
            [
                {"text": "🔄 Regenerate", "callback_data": f"regen:{draft_id}"},
                {"text": "❌ Skip", "callback_data": f"skip:{draft_id}"},
            ],
        ]
    }

    result = _api(
        "sendMessage",
        {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "Markdown",
            "reply_markup": keyboard,
            "disable_web_page_preview": True,
        },
    )
    return result["result"]["message_id"]


def edit_message(chat_id: str, message_id: int, new_text: str, draft_id: str) -> None:
    """Update existing Telegram message after text edit."""
    preview = new_text[:800] + ("…" if len(new_text) > 800 else "")
    message = f"📝 *Draft (edited)*\n\n{preview}"

    keyboard = {
        "inline_keyboard": [
            [
                {"text": "🚀 Post to LinkedIn", "callback_data": f"post:{draft_id}"},
                {"text": "✏️ Edit again", "callback_data": f"edit:{draft_id}"},
            ],
            [
                {"text": "❌ Skip", "callback_data": f"skip:{draft_id}"},
            ],
        ]
    }

    _api(
        "editMessageText",
        {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": message,
            "parse_mode": "Markdown",
            "reply_markup": keyboard,
        },
    )


def answer_callback(callback_query_id: str, text: str = "") -> None:
    _api("answerCallbackQuery", {"callback_query_id": callback_query_id, "text": text})


def send_text(chat_id: str, text: str) -> None:
    _api("sendMessage", {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"})
