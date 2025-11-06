import httpx
from config import settings

HEADERS = {
    "Authorization": f"Bearer {settings.PIPEFY_TOKEN}",
    "Content-Type": "application/json"
}

PIPEFY_URL = settings.PIPEFY_API_URL

async def find_card_by_email(client: httpx.AsyncClient, email: str) -> str | None:
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

async def update_card(client: httpx.AsyncClient, card_id: str, link: str) -> dict:
    mutation = {
        "query": f"""
            mutation {{
                updateCardField(input: {{ card_id: "{card_id}", field_id: "meeting_link" , new_value: "{link}" }}) {{
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
        return {"error": data["errors"]}
    
    if "data" in data and data["data"].get("updateCardField").get("card"):
        return {
            "message": "Card atualizado com sucesso",
            "card": data["data"]["updateCardField"]["card"]["id"],
        }
        
    return response.json()

async def create_or_update_card_pipefy(client: httpx.AsyncClient, lead: dict) -> dict:
          
    pipe_id = settings.PIPEFY_PIPE_ID  
    nome = lead.get("nome", "")
    email = lead.get("email", "")
    empresa = lead.get("empresa", "")
    necessidade = lead.get("necessidade", "")
    interesse_confirmado = "true" if lead.get("interesse_confirmado") else "false"

    create_mutation = {
        "query": f"""
            mutation{{
                createCard(
                    input:{{
                        pipe_id: {pipe_id},
                        fields_attributes: [
                            {{field_id: "nome", field_value: "{nome}"}},
                            {{field_id: "email", field_value: "{email}"}},
                            {{field_id: "empresa", field_value: "{empresa}"}},
                            {{field_id: "necessidade", field_value: "{necessidade}"}},
                            {{field_id: "interesse_confirmado", field_value: "{interesse_confirmado}"}}
                        ]
                    }}
                ){{
                    card{{
                        id
                        title
                    }}
                }}
            }}
        """
    }

    create_response = await client.post(PIPEFY_URL, headers=HEADERS, json=create_mutation)
    create_data = create_response.json()
    
    print("Create Card Response:", create_data)

    if "errors" in create_data:
        return {"error": create_data["errors"]}

    return {
        "message": "Card criado com sucesso",
        "card": create_data.get("data", {}).get("createCard", {}).get("card"),
    }
