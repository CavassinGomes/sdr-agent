from motor.motor_asyncio import AsyncIOMotorClient
from config import settings
from datetime import datetime

_client = None
_db = None

def get_db():
    global _client, _db

    if _client is None:
        _client = AsyncIOMotorClient(settings.MONGODB_URI)

    if _db is None:
        if hasattr(settings, "MONGODB_DB"):
            _db = _client[settings.MONGODB_DB]
        else:
            uri = settings.MONGODB_URI
            parts = uri.rsplit("/", 1)
            if len(parts) == 2 and parts[1]:
                _db = _client[parts[1]]
            else:
                raise ValueError(
                    "Nenhum nome de database encontrado em MONGODB_URI. "
                    "Adicione MONGODB_DB nas settings."
                )

    return _db


async def create_session_db(session_id: str, lead_email: str):
    db = get_db()
    await db.sessions.insert_one({
        "session_id": session_id,
        "lead_email": lead_email,
        "messages": [],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    })

async def update_session_lead_email(session_id: str, email: str):
    db = get_db()
    await db.sessions.update_one(
        {"session_id": session_id},
        {"$set": {"lead_email": email, "updated_at": datetime.utcnow()}}
    )

async def add_message_db(session_id: str, message: dict):
    db = get_db()
    await db.sessions.update_one(
        {"session_id": session_id},
        {
            "$push": {"messages": message},
            "$set": {"updated_at": datetime.utcnow()}
        }
    )


async def get_session_db(session_id: str):
    db = get_db()
    return await db.sessions.find_one({"session_id": session_id})
