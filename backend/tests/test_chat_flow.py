import pytest
import respx
import json
from unittest.mock import patch, AsyncMock
from datetime import datetime, timedelta
from typing import Dict, List, Any
from google.genai import types
from httpx import AsyncClient, ASGITransport
import httpx
import pytest_asyncio

from app import app
from routes.chat_routes import router as chat_router 
from services import ai_service, pipefy_service
from config import settings 
import services.calendar_service as calendar_service

@pytest.fixture(autouse=True)
def setup_settings(monkeypatch):
    monkeypatch.setattr(settings, "AI_API_KEY", "MOCKED_GEMINI_KEY")
    monkeypatch.setattr(settings, "AI_MODEL", "gemini-2.5-flash")
    monkeypatch.setattr(settings, "CALENDAR_BASE_URL", "http://mocked-calendar-api.com")
    monkeypatch.setattr(settings, "PIPEFY_API_URL", "http://mocked-pipefy-api.com/graphql")
    monkeypatch.setattr(settings, "PIPEFY_TOKEN", "MOCKED_PIPEFY_TOKEN")
    monkeypatch.setattr(settings, "PIPEFY_PIPE_ID", 12345)
    monkeypatch.setattr(settings, "CALENDAR_API_KEY", "MOCKED_CALENDAR_KEY")


@pytest_asyncio.fixture
async def ac_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


LEAD_DATA = {
    "nome": "João da Silva",
    "email": "joao.silva@exemplo.com",
    "empresa": "Tech Solutions Ltda",
    "necessidade": "Precisa de uma ferramenta para gerenciar tarefas e produtividade de equipes remotas.",
    "interesse_confirmado": True
}

SLOT_TIME = (datetime.utcnow() + timedelta(days=2, hours=10)).isoformat()
MOCKED_SLOTS = [
    {"id": 1, "start": SLOT_TIME, "end": (datetime.utcnow() + timedelta(days=2, hours=11)).isoformat()},
]

PIPEFY_SUCCESS_RESPONSE = {
    "message": "Card upserted successfully",
    "card": {"id": "CARD-456", "title": LEAD_DATA['nome']},
}


def create_gemini_call_response(function_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "candidates": [{
            "content": {
                "parts": [{
                    "function_call": {
                        "name": function_name,
                        "args": args
                    }
                }]
            }
        }]
    }

def create_gemini_text_response(text: str) -> Dict[str, Any]:
    return {
        "candidates": [{
            "content": {
                "parts": [{"text": text}]
            }
        }]
    }

@pytest.mark.asyncio
@patch.object(ai_service, 'chat_with_ai', new_callable=AsyncMock)
@respx.mock
async def test_full_agent_flow(mock_gemini, ac_client: AsyncClient):

    start_resp = await ac_client.post("/api/start-session")
    assert start_resp.status_code == 200
    session_id = start_resp.json()["session_id"]
    
    mock_gemini.side_effect = [
        create_gemini_text_response("Olá! Sou o agente de pré-vendas. Qual o seu nome e empresa?"),
    ]
    resp = await ac_client.post("/api/message", json={"session_id": session_id, "message": "Olá! Meu nome é João e sou da Tech Solutions."})
    print("\nFirst Message Response:", resp.json())
    assert "Qual o seu nome e empresa?" in resp.json()["reply"]

    mock_gemini.side_effect = [
        create_gemini_text_response("Perfeito, João. Qual o seu melhor email e qual a sua principal necessidade hoje?"),
    ]
    resp = await ac_client.post("/api/message", json={"session_id": session_id, "message": f"Meu email é {LEAD_DATA['email']} e preciso de um software de gestão de equipes."})
    assert "qual a sua principal necessidade hoje?" in resp.json()["reply"]


    mock_gemini.side_effect = [
        create_gemini_call_response("create_or_update_card_pipefy", {"lead": LEAD_DATA}),
        
        create_gemini_text_response("Obrigado, João. Seus dados foram registrados com sucesso no nosso sistema. Gostaria de agendar uma demonstração?"),
    ]
    
    pipefy_no_card_route = respx.post("http://mocked-pipefy-api.com/graphql").mock(
        side_effect=[
            httpx.Response(200, json={"data": {"findCards": {"edges": []}}}),
            httpx.Response(200, json={"data": {"createCard": {"card": {"id": "CARD-456", "title": LEAD_DATA['nome']}}}}),
        ]
    )

    pipefy_service.PIPEFY_URL = "http://mocked-pipefy-api.com/graphql"

    resp = await ac_client.post("/api/message", json={"session_id": session_id, "message": "Sim, tenho muito interesse!"})
    
    assert "Gostaria de agendar uma demonstração?" in resp.json()["reply"]
    assert any(a['action'] == 'create_or_update_card_pipefy' for a in resp.json()["actions"])
    
    mock_gemini.side_effect = [
        create_gemini_call_response("get_available_slots_next_7_days", {}),
        
        create_gemini_text_response(f"Tenho estes horários: {SLOT_TIME}, amanhã às 14h, ou depois de amanhã às 15h. Qual prefere?"),
    ]
    
    calendar_slots_route = respx.get("https://api.cal.com/v1/slots").mock(
        return_value=httpx.Response(200, json={"slots": MOCKED_SLOTS})
    )
    
    resp = await ac_client.post("/api/message", json={"session_id": session_id, "message": "Sim, quais são os horários disponíveis?"})

    assert "Qual prefere?" in resp.json()["reply"]
    assert any(a['action'] == 'get_available_slots_next_7_days' for a in resp.json()["actions"])
    
    mock_gemini.side_effect = [
        create_gemini_call_response("schedule_meeting", {"slot": MOCKED_SLOTS[0], "lead": LEAD_DATA}),
        
        create_gemini_text_response(f"Ótimo! Sua reunião foi agendada para {SLOT_TIME}. Você receberá um convite por e-mail."),
    ]
    
    calendar_booking_route = respx.post("https://api.cal.com/v1/bookings").mock(
        return_value=httpx.Response(200, json={"join_url": "https://meet.link/abc", "start_time": SLOT_TIME})
    )

    pipefy_update_route = respx.post("http://mocked-pipefy-api.com/graphql").mock(
        side_effect=[
            httpx.Response(200, json={"data": {"findCards": {"edges": [{"node": {"id": "CARD-456", "fields": []}}]}}}),
            httpx.Response(200, json={"data": {"updateCardField": {"card": {"id": "CARD-456", "title": LEAD_DATA['nome']}}}}),
        ]
    )

    resp = await ac_client.post("/api/message", json={"session_id": session_id, "message": f"Eu escolho o horário de {SLOT_TIME}"})
    
    assert "Você receberá um convite por e-mail." in resp.json()["reply"]
    assert any(a['action'] == 'schedule_meeting' for a in resp.json()["actions"])

    assert calendar_slots_route.called
    assert calendar_booking_route.called
    assert mock_gemini.call_count == 8