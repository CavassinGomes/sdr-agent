from datetime import datetime, timedelta
import uuid
from typing import Dict, Any
from config import settings


_sessions: Dict[str, Dict[str, Any]] = {}


def create_session() -> str:
    session_id = str(uuid.uuid4())
    _sessions[session_id] = {
    "messages": [],
    "created_at": datetime.utcnow(),
    "expires_at": datetime.utcnow() + timedelta(minutes=settings.SESSION_TIMEOUT)
    }
    return session_id


def get_session(session_id: str) -> dict | None:
    s = _sessions.get(session_id)
    if not s:
        return None
    if datetime.utcnow() > s["expires_at"]:
        _sessions.pop(session_id, None)
        return None
    return s


def add_message(session_id: str, message: dict) -> bool:
    s = get_session(session_id)
    if not s:
        return False
    s["messages"].append(message)
    s["expires_at"] = datetime.utcnow() + timedelta(minutes=settings.SESSION_TIMEOUT)
    return True


def end_session(session_id: str) -> None:
    _sessions.pop(session_id, None)