import httpx
from typing import Any, List, Dict
from config import settings
import json

HEADERS = {
    "Authorization": f"Bearer {settings.PIPEFY_TOKEN}",
    "Content-Type": "application/json"
}

PIPEFY_URL = settings.PIPEFY_API_URL

async def find_card_by_email(email: str) -> str | None:
    async with httpx.AsyncClient() as client:
        query = {
            "query": """
                query FindCards($pipe_id: ID!, $email: String!) {
                    findCards(pipeId: $pipe_id, search: {fieldId: "email", fieldValue: $email}){
                        edges{
                            node{
                                id
                                fields{
                                    name,
                                    value
                                }
                            }
                        }
                    }
                }
                    
            """,
            "variables": {
                "pipe_id": settings.PIPEFY_PIPE_ID,
                "email": email,
            },
        }

        response = await client.post(PIPEFY_URL, headers=HEADERS, json=query)
        data = response.json()

        if "data" in data and data["data"]["findCards"] and data["data"]["findCards"]["edges"]:
            edges = data["data"]["findCards"]["edges"]
            for edge in edges:
                card = edge["node"]
                return {"id": card["id"], "fields": card["fields"]}
        
        return {"error": "Card not found"}

async def update_card(client: httpx.AsyncClient, card_id: str, fields_to_update: List[Dict[str, str]]) -> dict:
    
    if not fields_to_update:
        return {"message": "Nenhum campo para atualizar."}

    results = []

    for field in fields_to_update:
        if field['field_id'] == 'email' or field['field_id'] == 'interesse_confirmado': continue
        mutation = {
            "query": f"""
                mutation {{
                    updateCardField(input: {{
                        card_id: "{card_id}",
                        field_id: "{field['field_id']}",
                        new_value: "{field['field_value']}"
                    }}) {{
                        card {{
                            id
                            title
                        }}
                    }}
                }}
            """
        }

        response = await client.post(PIPEFY_URL, headers=HEADERS, json=mutation)
        data = response.json()

        if "errors" in data:
            results.append({"field_id": field["field_id"], "error": data["errors"]})
        else:
            results.append({"field_id": field["field_id"], "status": "ok"})

    return {
        "message": "Processo concluído",
        "results": results
    }

async def upsert_lead_card(client: httpx.AsyncClient, lead: dict) -> dict:
    pipe_id = settings.PIPEFY_PIPE_ID
    email = lead.get("email", "")
    existing_card = await find_card_by_email(email)
    
    fields_data = [
        {"field_id": "nome", "field_value": lead.get("nome", "")},
        {"field_id": "email", "field_value": email},
        {"field_id": "empresa", "field_value": lead.get("empresa", "")},
        {"field_id": "necessidade", "field_value": lead.get("necessidade", "")},
        {"field_id": "interesse_confirmado", "field_value": "true" if lead.get("interesse_confirmado") else "false"},
        {"field_id": "meeting_link", "field_value": lead.get("meeting_link", "")},
        {"field_id": "meeting_datetime", "field_value": lead.get("meeting_datetime", "")},
    ]
    
    fields_data = [f for f in fields_data if f["field_value"]]
    
    if "id" in existing_card:
        card_id = existing_card["id"]
        
        fields_for_update_mutation = [
            {"field_id": f["field_id"], "field_value": f["field_value"]} 
            for f in fields_data
        ]
        
        return await update_card(client, card_id, fields_for_update_mutation)
    
    else:
        fields_attributes = [
            {"field_id": f["field_id"], "field_value": f["field_value"]} 
            for f in fields_data
        ]
        
        create_mutation = {
            "query": """
                mutation CreateCard($pipe_id: ID!, $fields: [FieldValueInput!]!) {
                    createCard(
                        input: {
                            pipe_id: $pipe_id,
                            fields_attributes: $fields
                        }
                    ) {
                        card {
                            id
                            title
                        }
                    }
                }
            """,
            "variables": {
                "pipe_id": pipe_id,
                "fields": fields_data
            }
        }

        create_response = await client.post(PIPEFY_URL, headers=HEADERS, json=create_mutation)
        create_data = create_response.json()

        if "errors" in create_data:
            return {"error": create_data["errors"]}

        return {
            "message": "Card criado com sucesso",
            "card": create_data.get("data", {}).get("createCard", {}).get("card"),
        }
        
async def create_or_update_card_pipefy(client: httpx.AsyncClient, lead: dict) -> dict:
    if client is None:
        async with httpx.AsyncClient() as client:
            return await upsert_lead_card(client, lead)
    else:
        return await upsert_lead_card(client, lead)

