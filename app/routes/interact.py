from fastapi import APIRouter, Request
from pydantic import BaseModel
import re
from services.booking_service import book_appointment

router = APIRouter()

booking_context = {}


class ChatRequest(BaseModel):
    message: str


@router.post("/interact")
def interact(req: ChatRequest, request: Request):
    user_id = request.client.host
    msg = req.message.lower().strip()
    msg = re.sub(r"[.,]", "", msg)

    if user_id not in booking_context:
        booking_context[user_id] = {
            "patient_name": None,
            "doctor": None,
            "time": None,
            "awaiting": None
        }

    ctx = booking_context[user_id]

    # -------- EXTRACTION --------

    if not ctx["patient_name"]:
        name_match = re.search(
            r"(?:my name is|name is)\s+([a-zA-Z]{2,})",
            msg
        )

        # allow plain name ONLY when awaiting name
        if not name_match and ctx.get("awaiting") == "name":
            name_match = re.fullmatch(r"[a-zA-Z]{2,}", msg)

        if name_match:
            # ✅ FIX: group(1) for search, group(0) for fullmatch
            ctx["patient_name"] = (
                name_match.group(1)
                if name_match.lastindex
                else name_match.group(0)
            ).capitalize()
            ctx["awaiting"] = None

    if not ctx["doctor"]:
        doctor_match = re.search(r"dr\s+([a-zA-Z]+)", msg)
        if doctor_match:
            ctx["doctor"] = f"Dr {doctor_match.group(1).capitalize()}"

    if not ctx["time"]:
        time_match = re.search(r"\b(\d{1,2})(?::|\.)?(\d{2})?\b", msg)
        if time_match:
            hour = time_match.group(1)
            minute = time_match.group(2) or "00"
            ctx["time"] = f"{hour}:{minute}"

    # -------- DECISION --------

    if not ctx["doctor"]:
        ctx["awaiting"] = "doctor"
        return {"reply": "Which doctor would you like to book?"}

    if not ctx["time"]:
        ctx["awaiting"] = "time"
        return {"reply": "Please tell me the appointment time."}

    if not ctx["patient_name"]:
        ctx["awaiting"] = "name"
        return {"reply": "Please tell me your name."}

    # -------- BOOKING --------

    data = {
        "patient_name": ctx["patient_name"],
        "doctor": ctx["doctor"],
        "date": "2025-01-15",  # temporary
        "time": ctx["time"]
    }

    success, message = book_appointment(data)

    booking_context.pop(user_id, None)

    return {"reply": message}
