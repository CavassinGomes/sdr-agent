from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class Lead(BaseModel):
    nome: str
    email: EmailStr
    empresa: Optional[str] = None
    necessidade: Optional[str] = None
    interesse_confirmado: bool = False
    meeting_link: Optional[str] = None
    meeting_datetime: Optional[datetime] = None