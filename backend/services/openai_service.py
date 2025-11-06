import os
from typing import List, Dict, Any
from openai import AsyncOpenAI
from config import settings

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

async def chat_with_openai(messages: List[Dict[str, Any]], functions: List[Dict[str, Any]] | None = None) -> Dict[str, Any]:
    params = {
        "model": settings.OPENAI_MODEL,
        "messages": messages,
        "temperature": 0.2,
    }
    
    if functions:
        params["functions"] = functions
        params["function_call"] = "auto"
    
    response = await client.chat.completions.create(**params)
    return response.model_dump()

def system_prompt_for_agent(product_desc: str) -> str:
    return (
        "You are a professional, empathetic pre-sales agent. "
        "Follow the business rules: ask discovery questions (name, company, need/pain, deadline), "
        "confirm explicit interest before offering scheduling, and when interest is confirmed call registrar functions. "
        f"Product info: {product_desc}"
    )