"""
State management via a private GitHub Gist.
No extra accounts or services needed — uses your existing GitHub token.
"""
import json
import uuid
from datetime import datetime, timezone

import requests

from src.config import GH_PAT

GIST_DESCRIPTION = "linkedin-post-scheduler-state"
GIST_FILENAME = "state.json"
_EMPTY_STATE = {"drafts": {}, "user_state": {}}

_headers = {"Authorization": f"token {GH_PAT}", "Accept": "application/vnd.github+json"}


def _find_gist_id() -> str | None:
    resp = requests.get("https://api.github.com/gists", headers=_headers, timeout=10)
    for g in resp.json():
        if g.get("description") == GIST_DESCRIPTION:
            return g["id"]
    return None


def _create_gist() -> str:
    resp = requests.post(
        "https://api.github.com/gists",
        headers=_headers,
        json={
            "description": GIST_DESCRIPTION,
            "public": False,
            "files": {GIST_FILENAME: {"content": json.dumps(_EMPTY_STATE)}},
        },
        timeout=10,
    )
    return resp.json()["id"]


def _get_gist_id() -> str:
    gist_id = _find_gist_id()
    return gist_id or _create_gist()


def _read_state() -> dict:
    gist_id = _get_gist_id()
    resp = requests.get(f"https://api.github.com/gists/{gist_id}", headers=_headers, timeout=10)
    content = resp.json()["files"][GIST_FILENAME]["content"]
    return json.loads(content)


def _write_state(state: dict) -> None:
    gist_id = _get_gist_id()
    requests.patch(
        f"https://api.github.com/gists/{gist_id}",
        headers=_headers,
        json={"files": {GIST_FILENAME: {"content": json.dumps(state, indent=2)}}},
        timeout=10,
    )


# ── Draft management ──────────────────────────────────────────────────────────

def save_draft(post_text: str, article: dict, telegram_message_id: int, chat_id: str) -> str:
    draft_id = str(uuid.uuid4())[:8]
    state = _read_state()
    state["drafts"][draft_id] = {
        "id": draft_id,
        "text": post_text,
        "article": article,
        "telegram_message_id": telegram_message_id,
        "chat_id": chat_id,
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    _write_state(state)
    return draft_id


def get_draft(draft_id: str) -> dict | None:
    return _read_state()["drafts"].get(draft_id)


def update_draft_text(draft_id: str, new_text: str) -> None:
    state = _read_state()
    if draft_id in state["drafts"]:
        state["drafts"][draft_id]["text"] = new_text
        _write_state(state)


def mark_draft_posted(draft_id: str) -> None:
    state = _read_state()
    if draft_id in state["drafts"]:
        state["drafts"][draft_id]["status"] = "posted"
        _write_state(state)


def mark_draft_skipped(draft_id: str) -> None:
    state = _read_state()
    if draft_id in state["drafts"]:
        state["drafts"][draft_id]["status"] = "skipped"
        _write_state(state)


# ── User interaction state (edit flow) ───────────────────────────────────────

def set_user_editing(user_id: int, draft_id: str) -> None:
    state = _read_state()
    state["user_state"][str(user_id)] = {"action": "editing", "draft_id": draft_id}
    _write_state(state)


def get_user_state(user_id: int) -> dict | None:
    return _read_state()["user_state"].get(str(user_id))


def clear_user_state(user_id: int) -> None:
    state = _read_state()
    state["user_state"].pop(str(user_id), None)
    _write_state(state)
