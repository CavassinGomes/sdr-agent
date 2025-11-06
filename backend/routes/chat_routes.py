from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Any, List
from utils.session_manager import create_session, get_session, add_message
from models.lead import Lead
from models.db import upsert_lead_db, get_lead_by_email
from services import openai_service, pipefy_service, calendar_service
from config import settings
import json

router = APIRouter()

class StartResponse(BaseModel):
    session_id: str

@router.post('/start-session', response_model=StartResponse)
async def start_session():
    sid = create_session()
    return {"session_id": sid}

class UserMessageIn(BaseModel):
    session_id: str
    message: str

class AssistantOut(BaseModel):
    reply: str
    actions: List[dict] | None = None


def build_messages(history: list, product_desc: str = "Product/Service description placeholder"):
    sys = {"role": "system", "content": openai_service.system_prompt_for_agent(product_desc)}
    return [sys] + history


@router.post('/message', response_model=AssistantOut)
async def message_endpoint(payload: UserMessageIn):
    session = get_session(payload.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or expired")
    
    add_message(payload.session_id, {"role": "user", "content": payload.message})
    messages = build_messages(session['messages'])

    functions = [
        {
            "name": "registrarLead",
            "description": "Register or update a lead in Pipefy and DB",
            "parameters": {
                "type": "object",
                "properties": {
                    "nome": {"type": "string"},
                    "email": {"type": "string"},
                    "empresa": {"type": "string"},
                    "necessidade": {"type": "string"},
                    "interesse_confirmado": {"type": "boolean"},
                    "meeting_link": {"type": ["string", "null"]},
                    "meeting_datetime": {"type": ["string", "null"]}
                },
                "required": ["nome", "email"]
            }
        },
        {
            "name": "oferecerHorarios",
            "description": "Return 2-3 available scheduling slots from the calendar provider",
            "parameters": {"type": "object", "properties": {}, "required": []}
        },
            {
                "name": "agendarReuniao",
                "description": "Schedule a meeting in the calendar provider using provided slot and lead",
                "parameters": {
                "type": "object",
                "properties": {
                    "slot": {"type": "object"},
                    "lead": {"type": "object"}
                },
                "required": ["slot", "lead"]
            }
        }
    ]

    oai_resp = await openai_service.chat_with_openai(messages=messages, functions=functions)

    choice = oai_resp.get('choices', [{}])[0]
    message_obj = choice.get('message', {})
    content = message_obj.get('content', '')

    function_call = message_obj.get('function_call')
    actions = []


    if function_call:
        fname = function_call.get('name')
        fargs_raw = function_call.get('arguments')
        try:
            fargs = {} if not fargs_raw else (json.loads(fargs_raw) if isinstance(fargs_raw, str) else fargs_raw)
        except Exception:
            fargs = {}


    if fname == 'registrarLead':
        lead_data = fargs
        await upsert_lead_db(lead_data)
        await pipefy_service.create_or_update_card_pipefy(lead_data)
        actions.append({"action":"registrarLead","status":"ok"})
        
        add_message(payload.session_id, {"role": "assistant", "content": "Lead registrado com sucesso."})
        content = "Obrigado — registrei seus dados. Posso oferecer horários para agendarmos a reunião."
    elif fname == 'oferecerHorarios':
        slots = await calendar_service.get_available_slots_next_7_days()
        offered = slots[:3]
        actions.append({"action":"oferecerHorarios","slots": offered})
        content = f"Posso oferecer os seguintes horários: {', '.join([s.get('start_time') for s in offered])}"
    elif fname == 'agendarReuniao':
        slot = fargs.get('slot')
        lead = fargs.get('lead')
        result = await calendar_service.schedule_meeting(slot, lead)
        lead['meeting_link'] = result.get('join_url') or result.get('htmlLink') or result.get('meeting_link')
        lead['meeting_datetime'] = result.get('start_time') or lead.get('meeting_datetime')
        await upsert_lead_db(lead)
        await pipefy_service.create_or_update_card_pipefy(lead)
        actions.append({"action":"agendarReuniao","status":"ok","meeting": result})
        content = "Reunião agendada com sucesso. Enviarei o link e o horário no card."


    add_message(payload.session_id, {"role": "assistant", "content": content})

    return {"reply": content, "actions": actions}