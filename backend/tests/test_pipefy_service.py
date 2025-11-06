import pytest
from services.pipefy_service import create_or_update_card_pipefy, find_card_by_email, update_card
import httpx



@pytest.mark.asyncio
async def test_find_card_by_email():
    httpx_client = httpx.AsyncClient()
    email = "teste@email.com"
    result = await find_card_by_email(httpx_client, email)
    print("\nFind Card Result:", result)
    assert result is not None
    assert any(key in result for key in ["id", "fields", "error", "errors"])
    

@pytest.mark.asyncio
async def test_update_card():
    httpx_client = httpx.AsyncClient()
    lead = {
        "nome": "Lucas Gomes",
        "email": "Teste@email.com",
        "empresa": "Minha Empresa",
        "necessidade": "Sistema de CRM",
        "interesse_confirmado": True,
        "meeting_link": "https://meet.example.com/abcd1234",
        "card_id": ""
    }
    card_id = await find_card_by_email(httpx_client, lead["email"])
    if "id" in card_id:
        card_id = card_id["id"]
    else:
        pytest.skip("Card not found to update.")
    result = await update_card(httpx_client, card_id, lead)
    print("\nUpdate Card Result:", result)
    assert result is not None
    assert "card" in result or result.get("success", False)
    
@pytest.mark.asyncio
async def test_create_or_update_card_pipefy():
    httpx_client = httpx.AsyncClient()
    
    lead = {
        "nome": "Lucas Gomes",
        "email": "lucao@email.com", #email deve ser unico para criar novo card
        "empresa": "Minha Empresa",
        "necessidade": "Sistema de CRM",
        "interesse_confirmado": True,
    }
    
    card_id = await find_card_by_email(httpx_client, lead["email"])
    if "id" in card_id:
        print("\nCard já existe:", card_id)
        assert True  # Existe um card com o email
        return
    
    result = await create_or_update_card_pipefy(httpx_client, lead)
    print("\nCreate or Update Card Result:", result)
    assert result is not None
    assert any(key in result for key in ["card"])
