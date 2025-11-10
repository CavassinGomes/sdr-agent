from motor.motor_asyncio import AsyncIOMotorClient
from config import settings
from datetime import datetime


client = AsyncIOMotorClient(settings.MONGODB_URI)
db = client[settings.MONGODB_URI.split("/")[-1]]


async def create_session_db(session_id: str, lead_email: str):
    await db.sessions.insert_one({
        "session_id": session_id,
        "lead_email": lead_email,
        "messages": [],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    })

async def update_session_lead_email(session_id: str, email: str):
    await db.sessions.update_one(
        {"session_id": session_id},
        {"$set": {"lead_email": email, "updated_at": datetime.utcnow()}}
    )

async def add_message_db(session_id: str, message: dict):
    await db.sessions.update_one(
        {"session_id": session_id},
        {
            "$push": {"messages": message},
            "$set": {"updated_at": datetime.utcnow()}
        }
    )


async def get_session_db(session_id: str):
    return await db.sessions.find_one({"session_id": session_id})
    