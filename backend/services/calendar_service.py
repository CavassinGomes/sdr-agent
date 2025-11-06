import httpx
from datetime import datetime, timedelta
from config import settings

BASE_URL = settings.CALENDAR_BASE_URL

async def get_available_slots_next_7_days() -> list:
    now = datetime.utcnow()
    end = now + timedelta(days=7)
    async with httpx.AsyncClient() as client:
        r = await client.get(
            f"{BASE_URL}/slots",
            params={
                "apiKey": settings.CALENDAR_API_KEY,
                "startTime": now.isoformat(),
                "endTime": end.isoformat(),
                "eventTypeId": 3758694,
            },
        )
        r.raise_for_status()
        data = r.json()
        slots = data.get("slots", [])
        
        if isinstance(slots, dict):
            slots = [slot for day_slots in slots.values() for slot in day_slots]

        return slots
        # return data.get("slots", [])


async def schedule_meeting(slot: dict, lead: dict) -> dict:
    try:
        payload = {
            "eventTypeId": 3758694,
            "start": slot["start"],
            "responses": {
                "name": lead.get("nome"),
                "email": lead.get("email"),
                "smsReminderNumber": "",
                "location": {
                    "value": "userPhone",
                    "optionValue": ""
                }
            },
            "timeZone": "America/Sao_Paulo",
            "language": "pt-BR",
            "title": f"Reunião entre {lead.get('nome')} e equipe de atendimento",
            "description": lead.get("necessidade"),
            "status": "PENDING",
            "metadata": {
                "empresa": lead.get("empresa"),
                "necessidade": lead.get("necessidade"),
            },
        }
        params = {
            "apiKey": settings.CALENDAR_API_KEY,
        }
        
        headers = {"Content-Type": "application/json"}
        async with httpx.AsyncClient() as client:
            r = await client.post(
                f"{BASE_URL}/bookings",
                headers=headers,
                json=payload,
                params=params
            )
            if r.status_code >= 400:
                print("\n❌ Erro ao agendar reunião!")
                print(f"Status: {r.status_code}")
                try:
                    print("Resposta JSON:", r.json())
                except Exception:
                    print("Resposta texto:", r.text)
                print("Payload enviado:", payload)
                print("Headers:", headers)
                print("Params:", params)

            r.raise_for_status()
            return r.json()

    except httpx.RequestError as e:
        print(f"🚫 Erro de conexão com a API: {e}")
    except httpx.HTTPStatusError as e:
        print(f"⚠️ Erro HTTP: {e.response.status_code}")
        print("Corpo do erro:", e.response.text)
    except Exception as e:
        print(f"💥 Erro inesperado: {e}")

    return {}

