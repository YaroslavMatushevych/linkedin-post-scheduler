"""
Vercel serverless function — Telegram webhook handler.
Handles: Post, Edit, Regenerate, Skip button callbacks + edit text replies.
"""
import json
import os
import sys

from http.server import BaseHTTPRequestHandler

# Add parent to path so we can import src
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.state import (
    get_draft,
    update_draft_text,
    mark_draft_posted,
    mark_draft_skipped,
    set_user_editing,
    get_user_state,
    clear_user_state,
)
from src.telegram_sender import answer_callback, send_text, edit_message
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

    if action == "post":
        answer_callback(cq_id, "Posting to LinkedIn…")
        try:
            post_to_linkedin(draft["text"])
            mark_draft_posted(draft_id)
            send_text(chat_id, f"✅ Posted to LinkedIn! Draft `{draft_id}`")
        except Exception as e:
            send_text(chat_id, f"❌ LinkedIn post failed: {e}")

    elif action == "edit":
        set_user_editing(user_id, draft_id)
        answer_callback(cq_id)
        send_text(
            chat_id,
            "✏️ Send me the new post text as a reply to this message.\n\n"
            "_Send /cancel to abort editing._",
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
        mark_draft_skipped(draft_id)
        answer_callback(cq_id, "Skipped.")
        send_text(chat_id, f"⏭ Draft `{draft_id}` skipped.")


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


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        self.send_response(200)
        self.end_headers()

        try:
            update = json.loads(body)
        except Exception:
            return

        if "callback_query" in update:
            handle_callback_query(update["callback_query"])
        elif "message" in update:
            handle_message(update["message"])

    def log_message(self, *args):
        pass  # suppress default HTTP logging
