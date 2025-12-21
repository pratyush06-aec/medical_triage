from fastapi import APIRouter, Request
from pydantic import BaseModel
import re

from services.booking_service import (
    book_appointment,
    # 🔧 MODIFICATION: import unavailable slot helper
    get_unavailable_slots
)

# =================================================
# ✅ TRIAGE + SPECIALTY INFERENCE (CORRECT)
# =================================================
from utils.emergency_support import (
    detect_emergency_level,
    infer_specialty_from_symptoms,
    format_sos_message,
    format_home_care
)

# =================================================
# ✅ CATALOG SERVICE (SINGLE SOURCE OF TRUTH)
# =================================================
from services.catalog_service import (
    get_doctor_catalog,
    group_doctors_with_schedule
)

# ❌ OLD DIRECT DB ACCESS (COMMENTED — DO NOT DELETE)
# from database.db import get_doctors_by_area_and_specialty

router = APIRouter()
booking_context = {}


class ChatRequest(BaseModel):
    message: str


# =================================================
# 🔧 MODIFICATION: HELPER TO FORMAT DOCTOR LIST FOR UI
# Prevents raw JSON / catalog dict from leaking
# =================================================
def format_doctor_list(doctors):
    response = ""
    for i, doc in enumerate(doctors, start=1):
        days = ", ".join(doc["schedule"].keys())
        response += f"{i}. {doc['name']} ({days})\n"
    return response


@router.post("/interact")
def interact(req: ChatRequest, request: Request):
    user_id = request.client.host
    msg = req.message.lower().strip()
    msg = re.sub(r"[.,]", "", msg)

    # ❌ OLD (BREAKS TIME SLOT MATCHING)
    # msg = msg.replace("-", " ")

    msg = re.sub(r"\s+", " ", msg)

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
    # ✅ NEW CONTEXT (TRIAGE + BOOKING + FALLBACK STATE)
    # =================================================
    if user_id not in booking_context:
        booking_context[user_id] = {
            "patient_name": None,
            "doctor": None,
            "time": None,
            "day": None,
            "awaiting": None,
            "available_doctors": None,
            "available_slots": None,  # 🔧 MODIFICATION: store filtered slots

            # ---- TRIAGE ----
            "emergency_checked": False,
            "emergency_level": None,
            "specialty": None,
            "fallback_specialty": None,
            "area": None,
            "symptom_text": None
        }

    ctx = booking_context[user_id]

    # =================================================
    # ✅ STEP 1: TRIAGE (GUARDED)
    # =================================================
    if not ctx["emergency_checked"] and ctx["awaiting"] is None:
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
    # ✅ STEP 2: BOOKING CONSENT
    # =================================================
    if ctx["awaiting"] == "booking_consent":
        if msg in ["yes", "y"]:
            ctx["awaiting"] = "area"
            return {"reply": "Please tell me your area of residence."}
        else:
            booking_context.pop(user_id, None)
            return {"reply": "Okay. Take care and monitor your symptoms."}

    # =================================================
    # ✅ STEP 3: AREA → SHOW CATALOG
    # =================================================
    if ctx["awaiting"] == "area":
        ctx["area"] = msg.lower()

        catalog_reply = get_doctor_catalog(
            area=ctx["area"],
            specialty=ctx["specialty"]
        )

        # =================================================
        # 🔧 MODIFICATION: HANDLE FALLBACK OFFER
        # =================================================
        if isinstance(catalog_reply, dict) and catalog_reply.get("type") == "fallback_offer":
            ctx["fallback_specialty"] = catalog_reply["fallback_specialty"]
            ctx["awaiting"] = "fallback_consent"

            return {
                "reply": (
                    f"❌ No {ctx['specialty'].replace('_',' ').title()} "
                    f"found in {ctx['area'].title()}.\n\n"
                    f"Would you like to consult a "
                    f"{ctx['fallback_specialty'].replace('_',' ').title()} instead? (yes/no)"
                )
            }

        # ❌ OLD (BROKEN): storing full catalog dict
        # ctx["available_doctors"] = catalog_reply

        # 🔧 MODIFICATION: extract doctor list ONLY
        doctors = catalog_reply["doctors"]
        ctx["available_doctors"] = doctors
        ctx["awaiting"] = "doctor_selection"

        return {
            "reply": (
                "🩺 **Available Doctors:**\n\n"
                f"{format_doctor_list(doctors)}\n\n"
                "Please choose a doctor by number."
            )
        }

    # =================================================
    # ✅ STEP 3.5: FALLBACK CONSENT
    # =================================================
    if ctx["awaiting"] == "fallback_consent":
        if msg in ["yes", "y"]:
            ctx["specialty"] = "general_physician"
            ctx["awaiting"] = "doctor_selection"
            ctx.pop("available_doctors", None)

            catalog_reply = get_doctor_catalog(
                area=ctx["area"],
                specialty=ctx["specialty"]
            )

            doctors = catalog_reply["doctors"]
            ctx["available_doctors"] = doctors

            return {
                "reply": (
                    "🩺 **Available General Physicians:**\n\n"
                    f"{format_doctor_list(doctors)}\n\n"
                    "Please choose a doctor by number."
                )
            }
        else:
            booking_context.pop(user_id, None)
            return {"reply": "Okay. Let me know if you need help later."}

    # =================================================
    # ✅ STEP 4: DOCTOR SELECTION
    # =================================================
    if ctx["awaiting"] == "doctor_selection":
        if not msg.isdigit():
            return {"reply": "Please enter the doctor number shown above."}

        try:
            index = int(msg) - 1
            ctx["doctor"] = ctx["available_doctors"][index]
            ctx["awaiting"] = "day_selection"
        except (ValueError, IndexError):
            return {"reply": "Please choose a valid doctor number."}

        days = ", ".join(ctx["doctor"]["schedule"].keys())
        return {
            "reply": (
                f"✅ You selected {ctx['doctor']['name']}.\n"
                f"Available days: {days}\n"
                "Please choose a day."
            )
        }

    # =================================================
    # ✅ STEP 5: DAY SELECTION (FILTER BOOKED SLOTS)
    # =================================================
    if ctx["awaiting"] == "day_selection":
        day = msg.title()
        if day not in ctx["doctor"]["schedule"]:
            return {"reply": "Please choose a valid available day."}

        ctx["day"] = day

        all_slots = ctx["doctor"]["schedule"][day]

        # 🔧 MODIFICATION: remove already-booked slots
        booked = get_unavailable_slots(ctx["doctor"]["name"], day)
        available_slots = [s for s in all_slots if s not in booked]

        if not available_slots:
            return {
                "reply": "❌ No available time slots on this day. Please choose another day."
            }

        ctx["available_slots"] = available_slots
        ctx["awaiting"] = "time_selection"
        slots = ", ".join(available_slots)

        return {
            "reply": f"Available time slots on {day}: {slots}\nChoose a time."
        }

    # =================================================
    # ✅ STEP 6: TIME SELECTION (FINAL, CORRECT VERSION)
    # =================================================
    if ctx["awaiting"] == "time_selection":

        # ❌ OLD (BROKEN): validated against full schedule
        # if msg not in ctx["doctor"]["schedule"][ctx["day"]]:
        #     return {"reply": "Please choose a valid time slot."}

        # 🔧 MODIFICATION: validate ONLY against filtered slots
        available_slots = ctx.get("available_slots", [])

        # normalize comparison
        user_time = msg.replace(" ", "")
        normalized_slots = [s.replace(" ", "") for s in available_slots]

        if user_time not in normalized_slots:
            return {"reply": "Please choose a valid available time slot."}

        ctx["time"] = available_slots[normalized_slots.index(user_time)]
        ctx["awaiting"] = "name"
        return {"reply": "Please tell me the patient name."}

    # =================================================
    # ❌ OLD REGEX PARSING (COMMENTED — DO NOT DELETE)
    # =================================================
    # doctor_match = re.search(r"dr\s+([a-zA-Z]+)", msg)
    # time_match = re.search(r"\b(\d{1,2})(?::|\.)?(\d{2})?\b", msg)

    # =================================================
    # ✅ STEP 7: PATIENT NAME → BOOK APPOINTMENT
    # =================================================
    if ctx["awaiting"] == "name":
        ctx["patient_name"] = msg.capitalize()

        data = {
            "patient_name": ctx["patient_name"],
            "doctor": ctx["doctor"]["name"],
            # "date": "2025-01-15",  # temporary
            "date": ctx["day"],
            "time": ctx["time"]
        }

        success, message = book_appointment(data)
        booking_context.pop(user_id, None)
        return {"reply": message}
