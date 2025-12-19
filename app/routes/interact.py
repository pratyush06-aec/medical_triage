from fastapi import APIRouter, Request
from pydantic import BaseModel
import re
from services.booking_service import book_appointment

# =================================================
# ✅ NEW: Emergency support imports (ADDED)
# =================================================
from utils.emergency_support import (
    detect_emergency_level,
    format_sos_message,
    format_home_care
)

router = APIRouter()

booking_context = {}

class ChatRequest(BaseModel):
    message: str


@router.post("/interact")
def interact(req: ChatRequest, request: Request):
    user_id = request.client.host
    msg = req.message.lower().strip()
    msg = re.sub(r"[.,]", "", msg)

    # =================================================
    # ❌ OLD CONTEXT INITIALIZATION (COMMENTED — DO NOT DELETE)
    # =================================================
    # if user_id not in booking_context:
    #     booking_context[user_id] = {
    #         "patient_name": None,
    #         "doctor": None,
    #         "time": None,
    #         "awaiting": None
    #     }

    # =================================================
    # ✅ NEW: CONTEXT WITH EMERGENCY FIELDS (MODIFIED)
    # =================================================
    if user_id not in booking_context:
        booking_context[user_id] = {
            "patient_name": None,
            "doctor": None,
            "time": None,
            "awaiting": None,
            "emergency_checked": False,   # NEW
            "emergency_level": None       # NEW
        }

    ctx = booking_context[user_id]

    # =================================================
    # ✅ NEW: TRIAGE LOGIC (ADDED)
    # Runs ONCE per conversation session
    # =================================================
    if not ctx["emergency_checked"]:
        level = detect_emergency_level(msg)
        ctx["emergency_level"] = level
        ctx["emergency_checked"] = True

        # 🚨 HIGH EMERGENCY → SOS RESPONSE → STOP FLOW
        if level == "HIGH":
            return {"reply": format_sos_message()}

        # 🩺 MODERATE / LOW → HOME CARE + ASK BOOKING CONSENT
        reply = format_home_care()
        reply += "\n\nWould you like to book an appointment? (yes/no)"
        ctx["awaiting"] = "booking_consent"
        return {"reply": reply}

    # =================================================
    # ✅ NEW: BOOKING CONSENT HANDLER (ADDED)
    # =================================================
    if ctx.get("awaiting") == "booking_consent":
        if msg in ["yes", "y"]:
            ctx["awaiting"] = None
            return {"reply": "Sure. Which doctor would you like to book?"}
        else:
            booking_context.pop(user_id, None)
            return {"reply": "Okay. Take care and monitor your symptoms."}

    # =================================================
    # -------- EXTRACTION (UNCHANGED LOGIC) --------
    # =================================================

    if not ctx["patient_name"]:
        name_match = re.search(
            r"(?:my name is|name is)\s+([a-zA-Z]{2,})",
            msg
        )

        # allow plain name ONLY when awaiting name
        if not name_match and ctx.get("awaiting") == "name":
            name_match = re.fullmatch(r"[a-zA-Z]{2,}", msg)

        if name_match:
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

    # =================================================
    # -------- DECISION (UNCHANGED LOGIC) --------
    # =================================================

    if not ctx["doctor"]:
        ctx["awaiting"] = "doctor"
        return {"reply": "Which doctor would you like to book?"}

    if not ctx["time"]:
        ctx["awaiting"] = "time"
        return {"reply": "Please tell me the appointment time."}

    if not ctx["patient_name"]:
        ctx["awaiting"] = "name"
        return {"reply": "Please tell me your name."}

    # =================================================
    # -------- BOOKING (UNCHANGED LOGIC) --------
    # =================================================

    data = {
        "patient_name": ctx["patient_name"],
        "doctor": ctx["doctor"],
        "date": "2025-01-15",  # temporary
        "time": ctx["time"]
    }

    success, message = book_appointment(data)

    booking_context.pop(user_id, None)

    return {"reply": message}
