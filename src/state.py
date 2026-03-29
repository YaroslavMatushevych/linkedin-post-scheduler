"""
State management via Upstash Redis REST API.
Stores draft posts and user interaction state.
"""
import json
import uuid
from datetime import datetime, timezone

import requests

from src.config import UPSTASH_REDIS_REST_URL, UPSTASH_REDIS_REST_TOKEN

DRAFT_TTL = 60 * 60 * 24 * 7  # 7 days


def _headers() -> dict:
    return {"Authorization": f"Bearer {UPSTASH_REDIS_REST_TOKEN}"}


def _set(key: str, value: str, ex: int | None = None) -> None:
    cmd = ["SET", key, value]
    if ex:
        cmd += ["EX", str(ex)]
    requests.post(UPSTASH_REDIS_REST_URL, json=cmd, headers=_headers(), timeout=5)


def _get(key: str) -> str | None:
    resp = requests.post(
        UPSTASH_REDIS_REST_URL,
        json=["GET", key],
        headers=_headers(),
        timeout=5,
    )
    return resp.json().get("result")


def _del(key: str) -> None:
    requests.post(UPSTASH_REDIS_REST_URL, json=["DEL", key], headers=_headers(), timeout=5)


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
    _set(f"draft:{draft_id}", json.dumps(draft), ex=DRAFT_TTL)
    return draft_id


def get_draft(draft_id: str) -> dict | None:
    raw = _get(f"draft:{draft_id}")
    return json.loads(raw) if raw else None


def update_draft_text(draft_id: str, new_text: str) -> None:
    draft = get_draft(draft_id)
    if draft:
        draft["text"] = new_text
        _set(f"draft:{draft_id}", json.dumps(draft), ex=DRAFT_TTL)


def mark_draft_posted(draft_id: str) -> None:
    draft = get_draft(draft_id)
    if draft:
        draft["status"] = "posted"
        _set(f"draft:{draft_id}", json.dumps(draft), ex=DRAFT_TTL)


def mark_draft_skipped(draft_id: str) -> None:
    draft = get_draft(draft_id)
    if draft:
        draft["status"] = "skipped"
        _set(f"draft:{draft_id}", json.dumps(draft), ex=DRAFT_TTL)


# ── User interaction state (for edit flow) ────────────────────────────────────

def set_user_editing(user_id: int, draft_id: str) -> None:
    _set(f"user_state:{user_id}", json.dumps({"action": "editing", "draft_id": draft_id}), ex=3600)


def get_user_state(user_id: int) -> dict | None:
    raw = _get(f"user_state:{user_id}")
    return json.loads(raw) if raw else None


def clear_user_state(user_id: int) -> None:
    _del(f"user_state:{user_id}")
