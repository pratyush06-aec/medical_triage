from fastapi import APIRouter, Request
from pydantic import BaseModel
import re

from services.booking_service import book_appointment

# =================================================
# ✅ MODIFIED IMPORTS (ADDED TRIAGE + SPECIALTY)
# =================================================
from utils.emergency_support import (
    detect_emergency_level,
    infer_specialty_from_symptoms,
    format_sos_message,
    format_home_care
)

# =================================================
# ✅ NEW IMPORTS FOR STEP 3 (ADDED)
# =================================================
from services.catalog_service import get_doctor_catalog
from database.db import get_doctors_by_area_and_specialty
from services.catalog_service import group_doctors_with_schedule

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
    # ✅ NEW CONTEXT WITH TRIAGE + CATALOG STATE
    # =================================================
    if user_id not in booking_context:
        booking_context[user_id] = {
            "patient_name": None,
            "doctor": None,
            "time": None,
            "day": None,
            "awaiting": None,
            "available_doctors": None,

            # ---- TRIAGE ----
            "emergency_checked": False,
            "emergency_level": None,
            "specialty": None,
            "area": None,
            "symptom_text": None
        }

    ctx = booking_context[user_id]

    # =================================================
    # ✅ TRIAGE LOGIC (UNCHANGED, CORRECT)
    # =================================================
    if not ctx["emergency_checked"]:
        ctx["symptom_text"] = msg
        ctx["emergency_level"] = detect_emergency_level(msg)
        ctx["specialty"] = infer_specialty_from_symptoms(msg)
        ctx["emergency_checked"] = True

        if ctx["emergency_level"] == "HIGH":
            return {"reply": format_sos_message()}

        reply = format_home_care()
        reply += "\n\nWould you like to book an appointment? (yes/no)"
        ctx["awaiting"] = "booking_consent"
        return {"reply": reply}

    # =================================================
    # ✅ BOOKING CONSENT
    # =================================================
    if ctx["awaiting"] == "booking_consent":
        if msg in ["yes", "y"]:
            ctx["awaiting"] = "area"
            return {"reply": "Please tell me your area of residence."}
        else:
            booking_context.pop(user_id, None)
            return {"reply": "Okay. Take care and monitor your symptoms."}

    # =================================================
    # ✅ AREA → SHOW CATALOG (STEP 3 ENTRY POINT)
    # =================================================
    if ctx["awaiting"] == "area":
        ctx["area"] = msg.lower()

        rows = get_doctors_by_area_and_specialty(
            ctx["area"], ctx["specialty"]
        )

        if not rows:
            return {
                "reply": f"No doctors found in {ctx['area']} for your concern."
            }

        ctx["available_doctors"] = group_doctors_with_schedule(rows)
        ctx["awaiting"] = "doctor_selection"

        return {
            "reply": get_doctor_catalog(
                area=ctx["area"],
                specialty=ctx["specialty"]
            )
        }

    # =================================================
    # ✅ DOCTOR SELECTION (BY NUMBER)
    # =================================================
    if ctx["awaiting"] == "doctor_selection":
        try:
            index = int(msg) - 1
            ctx["doctor"] = ctx["available_doctors"][index]
        except (ValueError, IndexError):
            return {"reply": "Please choose a valid doctor number."}

        ctx["awaiting"] = "day_selection"
        days = ", ".join(ctx["doctor"]["schedule"].keys())

        return {
            "reply": (
                f"You selected {ctx['doctor']['name']}.\n"
                f"Available days: {days}\n"
                "Please choose a day."
            )
        }

    # =================================================
    # ✅ DAY SELECTION
    # =================================================
    if ctx["awaiting"] == "day_selection":
        day = msg.title()

        if day not in ctx["doctor"]["schedule"]:
            return {"reply": "Please choose a valid available day."}

        ctx["day"] = day
        ctx["awaiting"] = "time_selection"

        slots = ", ".join(ctx["doctor"]["schedule"][day])
        return {
            "reply": f"Available time slots on {day}: {slots}\nChoose a time."
        }

    # =================================================
    # ✅ TIME SLOT SELECTION
    # =================================================
    if ctx["awaiting"] == "time_selection":
        if msg not in ctx["doctor"]["schedule"][ctx["day"]]:
            return {"reply": "Please choose a valid time slot."}

        ctx["time"] = msg
        ctx["awaiting"] = "name"
        return {"reply": "Please tell me the patient name."}

    # =================================================
    # ❌ OLD REGEX-BASED EXTRACTION (COMMENTED — DO NOT DELETE)
    # (Replaced by structured selection flow)
    # =================================================
    # doctor_match = re.search(r"dr\s+([a-zA-Z]+)", msg)
    # time_match = re.search(r"\b(\d{1,2})(?::|\.)?(\d{2})?\b", msg)

    # =================================================
    # ✅ PATIENT NAME
    # =================================================
    if ctx["awaiting"] == "name":
        ctx["patient_name"] = msg.capitalize()

        data = {
            "patient_name": ctx["patient_name"],
            "doctor": ctx["doctor"]["name"],
            "date": "2025-01-15",  # temporary
            "time": ctx["time"]
        }

        success, message = book_appointment(data)
        booking_context.pop(user_id, None)
        return {"reply": message}