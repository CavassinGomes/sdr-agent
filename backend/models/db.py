from motor.motor_asyncio import AsyncIOMotorClient
from config import settings
from datetime import datetime
from typing import Any, Dict

def create_motor_client() -> AsyncIOMotorClient:
    if not settings.MONGODB_URI:
        raise ValueError("MONGODB_URI não definida nas configurações.")
    return AsyncIOMotorClient(settings.MONGODB_URI)


async def create_session_db(session_id: str, lead_email: str):
    client = create_motor_client()
    try:
        db = client[settings.MONGODB_DB]
        await db.sessions.insert_one({
            "session_id": session_id,
            "lead_email": lead_email,
            "messages": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        })
    finally:
        client.close() 


async def update_session_lead_email(session_id: str, email: str):
    client = create_motor_client()
    try:
        db = client[settings.MONGODB_DB]
        await db.sessions.update_one(
            {"session_id": session_id},
            {"$set": {"lead_email": email, "updated_at": datetime.utcnow()}}
        )
    finally:
        client.close()

async def add_message_db(session_id: str, message: dict):
    client = create_motor_client()
    try:
        db = client[settings.MONGODB_DB]
        await db.sessions.update_one(
            {"session_id": session_id},
            {
                "$push": {"messages": message},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
    finally:
        client.close()

async def get_session_db(session_id: str) -> Dict[str, Any] | None:
    client = create_motor_client()
    try:
        db = client[settings.MONGODB_DB]
        return await db.sessions.find_one({"session_id": session_id})
    finally:
        client.close()