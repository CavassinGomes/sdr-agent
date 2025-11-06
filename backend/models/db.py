from motor.motor_asyncio import AsyncIOMotorClient
from config import settings


client = AsyncIOMotorClient(settings.MONGODB_URI)
db = client[settings.MONGODB_URI.split("/")[-1]]


async def upsert_lead_db(lead_dict: dict):
    await db.leads.update_one(
    {"email": lead_dict["email"]},
    {"$set": lead_dict},
    upsert=True
    )


async def get_lead_by_email(email: str):
    return await db.leads.find_one({"email": email})