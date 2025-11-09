from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class Lead(BaseModel):
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    empresa: Optional[str] = None
    necessidade: Optional[str] = None
    prazo: Optional[str] = None
    interesse_confirmado: bool = False
    meeting_link: Optional[str] = None
    meeting_datetime: Optional[datetime] = None