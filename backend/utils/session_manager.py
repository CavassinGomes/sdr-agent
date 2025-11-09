from datetime import datetime, timedelta
import uuid
from typing import Dict, Any
from config import settings
from models.lead import Lead


_sessions: Dict[str, Dict[str, Any]] = {}


def create_session() -> str:
    session_id = str(uuid.uuid4())
    _sessions[session_id] = {
    "messages": [],
    "created_at": datetime.utcnow(),
    "expires_at": datetime.utcnow() + timedelta(minutes=settings.SESSION_TIMEOUT),
    "stage": "initial",
    "lead": Lead(nome=None, email=None, empresa=None, necessidade=None, prazo=None, interesse_confirmado=False),
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
    
def update_lead_info(session_id: str, info: dict):
    session = _sessions.get(session_id)
    if not session:
        return None

    lead = session["lead"]
    stage = session["stage"]
    
    # 1. Atualiza todos os campos fornecidos, independentemente do stage.
    # Isso permite que o usuário corrija dados anteriores.
    if "nome" in info:
        lead.nome = info.get("nome")
    if "email" in info:
        lead.email = info.get("email")
    if "empresa" in info:
        lead.empresa = info.get("empresa")
    if "necessidade" in info:
        lead.necessidade = info.get("necessidade")
    if "prazo" in info:
        lead.prazo = info.get("prazo")
    
    if "interesse_confirmado" in info:
        lead.interesse_confirmado = info.get("interesse_confirmado", False)

    meeting_datetime_str = info.get("meeting_datetime")
    if meeting_datetime_str:
        try:
            lead.meeting_datetime = datetime.fromisoformat(meeting_datetime_str)
        except ValueError:
            pass
    
    if stage == "initial" and info.get("nome"):
        session["stage"] = "ask_email"
    
    elif stage == "ask_email" and info.get("email"):
        session["stage"] = "ask_empresa"
        
    elif stage == "ask_empresa" and info.get("empresa"):
        session["stage"] = "ask_necessidade"
        
    elif stage == "ask_necessidade" and info.get("necessidade"):
        session["stage"] = "ask_prazo"
        
    elif stage == "ask_prazo" and info.get("prazo"):
        session["stage"] = "confirm_interest"
    
    elif stage == "confirm_interest" and "interesse_confirmado" in info:
        lead.interesse_confirmado = info.get("interesse_confirmado", False)
        session["stage"] = "completed"
        
    return session