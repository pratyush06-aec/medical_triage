from fastapi import APIRouter
from pydantic import BaseModel
import re
from services.booking_service import book_appointment

router = APIRouter()


class ChatRequest(BaseModel):
    message: str


@router.post("/interact")
def interact(req: ChatRequest):
    msg = req.message.lower()

    # 🔍 very basic intent detection
    if "book" in msg and "dr" in msg:
        # VERY simple extraction (temporary)
        name_match = re.search(r"my name is (\w+)", msg)
        doctor_match = re.search(r"dr\s+(\w+)", msg)
        time_match = re.search(r"(\d{1,2}:\d{2})", msg)

        if not (name_match and doctor_match and time_match):
            return {
                "reply": "I need your name, doctor, and time to book the appointment."
            }

        data = {
            "patient_name": name_match.group(1).capitalize(),
            "doctor": f"Dr {doctor_match.group(1).capitalize()}",
            "date": "2025-01-15",   # temporary default
            "time": time_match.group(1)
        }

        success, message = book_appointment(data)
        return {"reply": message}

    # fallback (non-booking chat)
    return {
        "reply": "I can help you book appointments. Try saying: Book Dr Sharma tomorrow at 10:30."
    }
