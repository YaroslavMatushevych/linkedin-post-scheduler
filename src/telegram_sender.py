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
    # Telegram max is 4096 chars; leave room for the header/footer (~120 chars)
    preview = post_text[:3900] + ("…" if len(post_text) > 3900 else "")
    message = (
        f"📝 New LinkedIn draft\n\n"
        f"{preview}\n\n"
        f"🔗 Source: {article['title']}"
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
            "reply_markup": keyboard,
            "disable_web_page_preview": True,
        },
    )
    return result["result"]["message_id"]


def edit_message(chat_id: str, message_id: int, new_text: str, draft_id: str) -> None:
    """Update existing Telegram message after text edit or regeneration."""
    preview = new_text[:3900] + ("…" if len(new_text) > 3900 else "")
    message = f"📝 LinkedIn draft\n\n{preview}"

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

    _api(
        "editMessageText",
        {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": message,
            "reply_markup": keyboard,
        },
    )


def mark_message_done(chat_id: str, message_id: int) -> None:
    """Remove inline buttons from a message."""
    _api(
        "editMessageReplyMarkup",
        {
            "chat_id": chat_id,
            "message_id": message_id,
            "reply_markup": {"inline_keyboard": []},
        },
    )


def answer_callback(callback_query_id: str, text: str = "") -> None:
    # Non-fatal — callback queries can expire during cold starts; we still process the action
    try:
        _api("answerCallbackQuery", {"callback_query_id": callback_query_id, "text": text})
    except Exception:
        pass


def send_text(chat_id: str, text: str) -> None:
    _api("sendMessage", {"chat_id": chat_id, "text": text})
