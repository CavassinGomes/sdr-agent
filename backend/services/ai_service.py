import os
from typing import List, Dict, Any, Union
from google import genai
from google.genai import types
from config import settings
import re
import json

RESPONSE_SCHEMA = types.Schema(
    type=types.Type.OBJECT,
    properties={
        "reply": types.Schema(
            type=types.Type.STRING,
            description="A mensagem de texto que o agente deve enviar ao usuário."
        ),
        "info": types.Schema(
            type=types.Type.OBJECT,
            description="Objeto com os dados do lead coletados (nome, email, empresa, necessidade, prazo, interesse_confirmado).",
            properties={
                "nome": types.Schema(type=types.Type.STRING),
                "email": types.Schema(type=types.Type.STRING),
                "empresa": types.Schema(type=types.Type.STRING),
                "necessidade": types.Schema(type=types.Type.STRING),
                "prazo": types.Schema(type=types.Type.STRING),
                "interesse_confirmado": types.Schema(type=types.Type.BOOLEAN, description="True se o lead expressou interesse explícito no produto.")
            }
        )
    },
    required=["reply"]
)

async def chat_with_ai(messages: List[Dict[str, Any]], system_instructions: str, functions: List[Dict[str, Any]] | None = None) -> Dict[str, Any]:
    client = genai.Client(api_key=settings.AI_API_KEY)
    aclient = client.aio
    
    contents = []
    
    for msg in messages:
        role = msg.get("role")
        text_content = msg.get("content")
        
        if role and text_content:
            gemini_role = "model" if role == "assistant" else "user"
            contents.append(types.Content(role=gemini_role, parts=[{"text": text_content}]))
    
    tools = []
    if functions:
        for f in functions:
            func_decl = types.FunctionDeclaration(
                name=f["name"],
                description=f.get("description", ""),
                parameters=types.Schema(
                    **f.get("parameters", {"type": "object", "properties": {}, "required": []})
                )
            )
            tools.append(types.Tool(function_declarations=[func_decl]))

    generation_config = types.GenerateContentConfig(
        temperature=0.5,
        tools=tools if tools else None,
        system_instruction=system_instructions,
        **(
            {} if tools else {
                "response_mime_type": "application/json",
                "response_schema": RESPONSE_SCHEMA
            }
        )
    )
    
    response = await aclient.models.generate_content(
        model=settings.AI_MODEL,
        contents=contents,
        config=generation_config
    )
    
    
    try:
        if not functions:
            raw_text = response.text.strip()
            parsed = json.loads(raw_text)
            
            if "reply" in parsed:
                return parsed
            else:
                return {"reply": raw_text}
        else:
            return response

    except json.JSONDecodeError as e:
        print(f"ERRO CRÍTICO DE JSON DECODE (JSON MODE): {e}")
        return {"reply": response.text or "Erro ao processar resposta do modelo."}

def system_prompt_for_agent(product_desc: str) -> str:
    return (
        "Você é um assistente de pré-vendas virtual chamado **Assistente Virtual Selly-IA** e sempre deve se apresentar ao iniciar a conversa e conduzir o usuário durante todo o processo de vendas de sistemas.\n"
        "Lembrando estamos vendendo um serviço de software sob medida para empresas.\n\n"
        "Seu objetivo é conduzir o usuário em uma conversa natural, "
        "fazendo uma pergunta de cada vez com base nas respostas anteriores.\n\n"

        "🧭 **Fluxo da conversa:**\n"
        "1️⃣ Cumprimente e pergunte o nome. (apos isso, nao se apresente novamente)\n"
        "2️⃣ Pergunte o e-mail do cliente.\n"
        "3️⃣ Pergunte o nome da empresa.\n"
        "4️⃣ Pergunte a necessidade ou dor do cliente.\n"
        "5️⃣ Pergunte o prazo para a solução.\n"
        "6️⃣ Resuma o entendimento e pergunte se pode agendar uma reunião.\n"
        "7️⃣ A frase de confirmacao deve ser explicita e **no momento que o cliente confirmar claramente** que deseja prosseguir com o agendamento, "
        "você deve chamar as funções necessárias nesta ordem:\n"
        "   - `create_or_update_card_pipefy` → cria ou atualiza o lead no Pipefy e `get_available_slots_next_7_days` → busca os próximos horários disponíveis e apresenta ao cliente.\n"
        " No momento da confirmacao do interesse voce deve em todas as vezes chamar as 2 funcoes mencionadas anteriormente e nao deve dar uma resposta sem as chamadas de funcao configuradas.\n"
        " A funcao create_or_update_card_pipefy, deve ser chamada quando o cliente confirmar interesse ou quando a conversa for finalizada sem interesse, e devera ser utilizada para atualizar o meeting_link assim que confirmada a reunião.\n"
        " Nao tem a necessidade de perguntar novamente dados do cliente, ao chegar nesse ponto, crie o card no pipefy e busque os horarios disponiveis.\n"
        " Execute a funcao get_available_slots_next_7_days, sempre que o cliente confirmar interesse em agendar uma reunião e exatamente no momento da confirmacao.\n"
        "   - Após o cliente escolher um horário, chame `schedule_meeting` para confirmar o agendamento e `create_or_update_card_pipefy` novamente para atualizar o lead no Pipefy com o meeting_link(isso e importante).\n\n"

        "⚠️ **Importante:** nunca envie todas as perguntas de uma vez. "
        "Espere a resposta do usuário antes de continuar.\n"
        "Sempre que novas informações forem descobertas, envie-as também no formato JSON:\n\n"
        '{"text": "Perfeito, {nome}! Qual é o nome da sua empresa?", "info": {"nome": "{nome}"}}\n\n'
        "Os campos possíveis no objeto `info` são: nome, email, empresa, necessidade, prazo e interesse_confirmado.\n\n"

        "💡 **Comportamento esperado:**\n"
        "- Seja simpático, claro e direto.\n"
        "- Se o cliente disser algo que indica interesse em prosseguir (ex: 'sim', 'vamos agendar', 'quero marcar'), "
        "chame `create_or_update_card_pipefy` e em seguida `get_available_slots_next_7_days`.\n"
        "- Quando o cliente escolher um horário, chame `schedule_meeting`.\n"
        "- Após o agendamento, confirme a reunião com o link e horário.\n"
        "- Se o cliente não demonstrar interesse, chame `create_or_update_card_pipefy` com `interesse_confirmado` como False e finalize a conversa cordialmente.\n\n"
        "Se o cliente não fornecer uma informação necessária, pergunte educadamente por ela.\n\n"
    )
    