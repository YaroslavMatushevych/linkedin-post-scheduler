"""
State management via Redis Cloud.
Stores draft posts and user interaction state.
"""
import json
import uuid
from datetime import datetime, timezone

import redis

from src.config import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD

DRAFT_TTL = 60 * 60 * 24 * 7  # 7 days


def _client() -> redis.Redis:
    return redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD,
        username="default",
        decode_responses=True,
        socket_timeout=5,
    )


# ── Draft management ──────────────────────────────────────────────────────────

def save_draft(post_text: str, article: dict, telegram_message_id: int, chat_id: str) -> str:
    draft_id = str(uuid.uuid4())[:8]
    draft = {
        "id": draft_id,
        "text": post_text,
        "article": article,
        "telegram_message_id": telegram_message_id,
        "chat_id": chat_id,
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    r = _client()
    r.set(f"draft:{draft_id}", json.dumps(draft), ex=DRAFT_TTL)
    return draft_id


def get_draft(draft_id: str):
    raw = _client().get(f"draft:{draft_id}")
    return json.loads(raw) if raw else None


def update_draft_text(draft_id: str, new_text: str) -> None:
    draft = get_draft(draft_id)
    if draft:
        draft["text"] = new_text
        _client().set(f"draft:{draft_id}", json.dumps(draft), ex=DRAFT_TTL)


def mark_draft_posted(draft_id: str) -> None:
    draft = get_draft(draft_id)
    if draft:
        draft["status"] = "posted"
        _client().set(f"draft:{draft_id}", json.dumps(draft), ex=DRAFT_TTL)


def mark_draft_skipped(draft_id: str) -> None:
    draft = get_draft(draft_id)
    if draft:
        draft["status"] = "skipped"
        _client().set(f"draft:{draft_id}", json.dumps(draft), ex=DRAFT_TTL)


# ── User interaction state (for edit flow) ────────────────────────────────────

def set_user_editing(user_id: int, draft_id: str) -> None:
    _client().set(
        f"user_state:{user_id}",
        json.dumps({"action": "editing", "draft_id": draft_id}),
        ex=3600,
    )


def get_user_state(user_id: int):
    raw = _client().get(f"user_state:{user_id}")
    return json.loads(raw) if raw else None


def clear_user_state(user_id: int) -> None:
    _client().delete(f"user_state:{user_id}")
