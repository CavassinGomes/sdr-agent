import pytest
from models import lead
from services.calendar_service import get_available_slots_next_7_days, schedule_meeting


@pytest.mark.asyncio
async def test_get_available_slots_next_7_days():
    slots = await get_available_slots_next_7_days()
    print("\nAvailable Slots:", slots)
    assert isinstance(slots, list)
    assert all('time' in s for s in slots)


@pytest.mark.asyncio
async def test_schedule_meeting():
    lead = {
        "nome": "Lucas Gomes",
        "email": "lucascavassinig@gmail.com",
        "empresa": "Minha Empresa",
        "necessidade": "Sistema de CRM",
        "interesse_confirmado": True
    }
    slot = {"start": "2025-11-30T12:00:00Z"}
    result = await schedule_meeting(slot, lead)
    assert result is not None
    assert "attendees" in result
    assert result.get("status") in ["ACCEPTED", "PENDING", "CANCELLED", "REJECTED"]