from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Any, List, Dict
from utils.session_manager import create_session, get_session, add_message, end_session, update_lead_info
from services import ai_service, pipefy_service, calendar_service
from google.genai import types
from models.db import add_message_db, create_session_db, update_session_lead_email
import json

router = APIRouter()

class StartResponse(BaseModel):
    session_id: str
    messages: str

@router.post("/start-session", response_model=StartResponse)
async def start_session():
    sid = create_session()
    await create_session_db(session_id=sid, lead_email="")
    
    init_prompt = ai_service.system_prompt_for_agent("Sistema de CRM e gestão comercial")
    
    ai_response = await ai_service.chat_with_ai(
        messages=[{"role": "system", "content": init_prompt}],
        system_instructions=init_prompt
    )
    await add_message_db(sid, {"role": "assistant", "content": ai_response.get("reply", '')})
    
    return {
        "session_id": sid,
        "messages": ai_response.get("reply", "")
    }

class UserMessageIn(BaseModel):
    session_id: str
    message: str

class AssistantOut(BaseModel):
    reply: str
    actions: List[dict] | None = None
    
PRODUCT_DESCRIPTION = "Nossa solução é um software de gestão de equipes de alta performance que integra comunicação, tarefas e análise de produtividade em uma única plataforma."

def build_message(history: List[Dict[str, Any]]):
    system_instructions = ai_service.system_prompt_for_agent(PRODUCT_DESCRIPTION)
    
    return history, system_instructions

def get_gemini_functions_schema() -> List[Dict[str, Any]]:
    return [
        {
            "name": "create_or_update_card_pipefy",
            "description": "Cria/atualiza um card de Lead no Pipefy com as informações coletadas (nome, email, empresa, necessidade, interesse_confirmado, meeting_link). Esta função deve ser chamada quando o cliente confirmar interesse ou quando a conversa for finalizada sem interesse, e devera ser utilizada para atualizar o meeting_link assim que confirmada a reunião.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lead": {"type": "object", "description": "Um dicionário contendo informações do lead: 'nome', 'email', 'empresa', 'necessidade', 'prazo', 'interesse_confirmado', 'meeting_link'."},
                },
                "required": ["lead"],
            },
        },
       {
            "name": "get_available_slots_next_7_days",
            "description": "Busca os horários disponíveis para agendamento de reuniões nos próximos 7 dias. Use esta função apenas quando o usuário confirmar explicitamente o interesse.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
        {
            "name": "schedule_meeting",
            "description": "Agenda uma reunião de pré-vendas. Deve ser chamada imediatamente após o usuário confirmar o interesse e escolher um slot de horário. Garanta que o 'slot' e 'lead' tenham todas as informações necessárias antes de chamar.",
            "parameters": {
                "type": "object",
                "properties": {
                    "slot": {"type": "object", "description": "O objeto do slot de horário escolhido, retornado por 'get_available_slots_next_7_days', deve conter 'start' (horário de início no formato ISO 8601)."},
                    "lead": {"type": "object", "description": "Um dicionário contendo informações do lead: 'nome', 'email', 'empresa', 'necessidade'."},
                },
                "required": ["slot", "lead"],
            },
        },
    ]
    
@router.post("/message", response_model=AssistantOut)
async def message_endpoint(payload: UserMessageIn):
    session = get_session(payload.session_id)
    if not session:
        return JSONResponse(status_code=404, content={"detail": "Session not found or expired."})

    add_message(payload.session_id, {"role": "user", "content": payload.message})
    await add_message_db(payload.session_id, {"role": "user", "content": payload.message})
    
    messages, system_instructions = build_message(session['messages'])

    functions = None

    if session['stage'] == "completed":
        functions = get_gemini_functions_schema()

    gemini_resp = await ai_service.chat_with_ai(
        messages=messages,
        system_instructions=system_instructions,
        functions=functions
    )
    await add_message_db(payload.session_id, {"role": "assistant", "content": gemini_resp.get("reply", '')})
    
    if "info" in gemini_resp:
        update_lead_info(payload.session_id, gemini_resp["info"])
        if "email" in gemini_resp["info"]:
            await update_session_lead_email(payload.session_id, gemini_resp["info"]["email"])

    if session['stage'] == "completed" and functions is None:
        gemini_resp = None
        functions = get_gemini_functions_schema()
        gemini_resp = await ai_service.chat_with_ai(
            messages=messages,
            system_instructions=system_instructions,
            functions=functions
        )
        await add_message_db(payload.session_id, {"role": "assistant", "content": gemini_resp.get("reply", '')})

    text_content, actions = "", []
    if functions:
        text_content, actions = await process_ai_response(payload.session_id, gemini_resp)

    if session['stage'] != "completed" and not text_content:
        text_content = gemini_resp.get("reply", '')


    if actions:
        for action in actions:
            add_message(payload.session_id, {"role": "assistant", "content": f"Action: {action['action']}, Result: {action['result']}"})
            await add_message_db(payload.session_id, {"role": "assistant", "content": f"Action: {action['action']}, Result: {action['result']}"})
        
        messages, system_instructions = build_message(session['messages'])
        gemini_resp = await ai_service.chat_with_ai(
            messages=messages,
            system_instructions=system_instructions,
            functions=None
        )
        final_reply = gemini_resp.get("reply", '')
        if final_reply:
            add_message(payload.session_id, {"role": "assistant", "content": final_reply})
            await add_message_db(payload.session_id, {"role": "assistant", "content": gemini_resp.get("reply", '')})
            text_content += final_reply
        return {"reply": text_content, "actions": actions}
        
    return {"reply": text_content, "actions": actions}
    
async def process_ai_response(session_id: str, gemini_resp: dict):
    actions = []
    text_content = ""
    

    first_candidate = gemini_resp.candidates[0]
    content_len = len(first_candidate.content.parts)
    for i in range(content_len):
        
        parts = first_candidate.content.parts[i]

        function_calls = parts.function_call
        text_content = parts.text or ""

        if function_calls:

           
            fname = function_calls.name
            fargs = dict(function_calls.args)
            function_result = None

            if fname == 'create_or_update_card_pipefy':
                lead_data = fargs['lead']
                result = await pipefy_service.create_or_update_card_pipefy(client=None, lead=lead_data)
                function_result = {"status": "sucesso", "card_id": result.get('card', {}).get('id', 'N/A')}
                actions.append({"action": fname, "result": result})

            elif fname == 'get_available_slots_next_7_days':
                slots = await calendar_service.get_available_slots_next_7_days()
                offered = slots[:3]
                function_result = {"available_slots": offered}
                actions.append({"action": fname, "result": offered})

            elif fname == 'schedule_meeting':
                slot = fargs.get('slot', {})
                lead = fargs.get('lead', {})
                result = await calendar_service.schedule_meeting(slot, lead)
                
                if result['data']['meetingUrl'] is None:
                    function_result = {"status": "falha", "meeting_link": None, "datetime": None}
                    actions.append({"action": fname, "result": function_result})
                    continue
                
                meeting_link = result['data']['meetingUrl']
                meeting_datetime = slot.get('time')

                lead['meeting_link'] = meeting_link
                lead['meeting_datetime'] = meeting_datetime
                await pipefy_service.create_or_update_card_pipefy(client=None, lead=lead)
            
                function_result = {"status": "sucesso", "meeting_link": meeting_link, "datetime": meeting_datetime}
                actions.append({"action": fname, "result": function_result})

    return text_content, actions