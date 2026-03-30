"""
WSGI entrypoint for Vercel. All requests are routed here.
Handles Telegram webhook at POST /api/webhook.
"""
import json
import os
import sys
import traceback

sys.path.insert(0, os.path.dirname(__file__))

from src.state import (
    get_draft,
    update_draft_text,
    mark_draft_posted,
    mark_draft_skipped,
    set_user_editing,
    get_user_state,
    clear_user_state,
)
from src.telegram_sender import answer_callback, send_text, edit_message, mark_message_done
from src.linkedin_api import post_to_linkedin
from src.generator import generate_post


def handle_callback_query(cq: dict) -> None:
    cq_id = cq["id"]
    data = cq.get("data", "")
    user_id = cq["from"]["id"]
    chat_id = str(cq["message"]["chat"]["id"])
    message_id = cq["message"]["message_id"]

    if ":" not in data:
        answer_callback(cq_id, "Unknown action")
        return

    action, draft_id = data.split(":", 1)
    draft = get_draft(draft_id)

    if not draft:
        answer_callback(cq_id, "⚠️ Draft expired or not found.")
        return

    # Always answer the callback FIRST — must happen within seconds of button press
    if action == "post":
        answer_callback(cq_id, "Posting to LinkedIn…")
        try:
            post_to_linkedin(draft["text"])
            mark_draft_posted(draft_id)
            mark_message_done(chat_id, message_id)
            send_text(chat_id, "✅ Posted to LinkedIn!")
        except Exception as e:
            send_text(chat_id, f"❌ LinkedIn post failed: {e}")

    elif action == "edit":
        answer_callback(cq_id)
        set_user_editing(user_id, draft_id)
        current_preview = draft["text"][:1000] + ("…" if len(draft["text"]) > 1000 else "")
        send_text(
            chat_id,
            f"✏️ Current draft:\n\n{current_preview}\n\nSend me the updated text now. Send /cancel to abort.",
        )

    elif action == "regen":
        answer_callback(cq_id, "Regenerating…")
        try:
            new_text = generate_post(draft["article"])
            update_draft_text(draft_id, new_text)
            edit_message(chat_id, message_id, new_text, draft_id)
        except Exception as e:
            send_text(chat_id, f"❌ Regeneration failed: {e}")

    elif action == "skip":
        answer_callback(cq_id, "Skipped.")
        try:
            mark_draft_skipped(draft_id)
            mark_message_done(chat_id, message_id)
            send_text(chat_id, "⏭ Draft skipped.")
        except Exception as e:
            send_text(chat_id, f"❌ Skip failed: {e}")


def handle_message(message: dict) -> None:
    user_id = message["from"]["id"]
    chat_id = str(message["chat"]["id"])
    text = message.get("text", "").strip()

    if text == "/cancel":
        clear_user_state(user_id)
        send_text(chat_id, "Edit cancelled.")
        return

    state = get_user_state(user_id)
    if state and state.get("action") == "editing":
        draft_id = state["draft_id"]
        draft = get_draft(draft_id)
        if draft:
            update_draft_text(draft_id, text)
            clear_user_state(user_id)
            edit_message(chat_id, draft["telegram_message_id"], text, draft_id)
            send_text(chat_id, "✅ Draft updated! Use the buttons above to post or edit again.")
        else:
            clear_user_state(user_id)
            send_text(chat_id, "⚠️ Draft not found (may have expired).")


def app(environ, start_response):
    path = environ.get("PATH_INFO", "")
    method = environ.get("REQUEST_METHOD", "")

    # Debug: verify env vars are loaded and Telegram works
    if path == "/debug" and method == "GET":
        env_keys = [k for k in ["TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID", "REDIS_HOST", "REDIS_PASSWORD", "GEMINI_API_KEY"] if os.environ.get(k)]
        try:
            send_text(os.environ.get("TELEGRAM_CHAT_ID", ""), f"✅ wsgi.py alive. Env vars: {env_keys}")
            msg = f"OK: {env_keys}"
        except Exception as e:
            msg = f"send_text failed: {e}"
        start_response("200 OK", [("Content-Type", "text/plain")])
        return [msg.encode()]

    if path == "/api/webhook" and method == "POST":
        length = int(environ.get("CONTENT_LENGTH", 0) or 0)
        body = environ["wsgi.input"].read(length)

        try:
            update = json.loads(body)
            if "callback_query" in update:
                handle_callback_query(update["callback_query"])
            elif "message" in update:
                handle_message(update["message"])
        except Exception as e:
            try:
                send_text(
                    os.environ.get("TELEGRAM_CHAT_ID", ""),
                    f"❌ Webhook crash:\n{type(e).__name__}: {e}\n\n{traceback.format_exc()[-500:]}",
                )
            except Exception:
                pass

    start_response("200 OK", [("Content-Type", "text/plain")])
    return [b"OK"]
