from fastapi import APIRouter, Request
from pydantic import BaseModel
import re

# =================================================
# 🔧 IMPORT BOOKING / CANCEL / LOOKUP HELPERS
# =================================================
from services.booking_service import (
    book_appointment_with_user,
    get_unavailable_slots,
    get_patient_appointments,  # ❌ LEGACY – preserved
    cancel_appointment          # ❌ LEGACY – preserved
)

# =================================================
# ✅ MODIFICATION: USER-SCOPED PROFILE HELPERS
# =================================================
from services.profile_service import (
    get_user_active_appointments,
    cancel_appointment_db
)

# =================================================
# TRIAGE + SPECIALTY INFERENCE
# =================================================
from utils.emergency_support import (
    detect_emergency_level,
    infer_specialty_from_symptoms,
    format_sos_message,
    format_home_care
)

# =================================================
# CATALOG SERVICE
# =================================================
from services.catalog_service import get_doctor_catalog

router = APIRouter()
booking_context = {}


class ChatRequest(BaseModel):
    message: str

SPECIALTY_MAP = {
    "cardiology": "cardiologist",
    "neurology": "neurologist",
    "gastroenterology": "gastroenterologist",
    "general": "general_physician",
}

# =================================================
# 🔧 FORMAT DOCTOR LIST
# =================================================
def format_doctor_list(doctors):
    response = ""
    for i, doc in enumerate(doctors, start=1):
        days = ", ".join(doc["schedule"].keys())
        response += f"{i}. {doc['name']} ({days})\n"
    return response


# =================================================
# 🔧 FORMAT APPOINTMENTS LIST
# ❌ LEGACY — PRESERVED (NOT USED ANYMORE)
# =================================================
def format_appointments_list(appts):
    response = ""
    for i, a in enumerate(appts, start=1):
        response += f"{i}. {a[1]} — {a[2]} — {a[3]}\n"
    return response


@router.post("/interact")
def interact(req: ChatRequest, request: Request):

    # =================================================
    # ✅ SESSION AUTH (SINGLE SOURCE OF TRUTH)
    # =================================================
    user = request.session.get("user")
    if not user:
        return {"reply": "❌ Please log in to continue."}

    user_id = user["id"]

    msg = req.message.lower().strip()
    msg = re.sub(r"[.,]", "", msg)
    msg = re.sub(r"\s+", " ", msg)

    # =================================================
    # 🔧 CONTEXT INITIALIZATION
    # =================================================
    if user_id not in booking_context:
        booking_context[user_id] = {
            "patient_name": None,
            "doctor": None,
            "time": None,
            "day": None,
            "awaiting": None,
            "available_doctors": None,
            "available_slots": None,
            "mode": None,
            "appointments": None,
            "selected_appointment": None,
            "rescheduling": False,
            "emergency_checked": False,
            "emergency_level": None,
            "specialty": None,
            "fallback_specialty": None,
            "area": None,
            "symptom_text": None
        }

    ctx = booking_context[user_id]

    # =================================================
    # TRIAGE (RUNS ONCE)
    # =================================================
    if not ctx["emergency_checked"] and ctx["awaiting"] is None:
        ctx["symptom_text"] = msg
        ctx["emergency_level"] = detect_emergency_level(msg)
        ctx["specialty"] = infer_specialty_from_symptoms(msg)
        ctx["specialty"] = SPECIALTY_MAP.get(ctx["specialty"], ctx["specialty"])
        ctx["emergency_checked"] = True

        if ctx["emergency_level"] == "HIGH":
            return {"reply": format_sos_message()}

        ctx["awaiting"] = "action_selection"
        return {
            "reply": (
                f"{format_home_care()}\n\n"
                "What would you like to do?\n"
                "1️⃣ Book new appointment\n"
                "2️⃣ Reschedule appointment\n"
                "3️⃣ Cancel appointment"
            )
        }

    # =================================================
    # ACTION SELECTION
    # =================================================
    if ctx["awaiting"] == "action_selection":

        if msg == "1":
            # ✅ FIX: clean only booking-related fields, keep ctx intact
            ctx["mode"] = "book"
            ctx["awaiting"] = "booking_consent"

            ctx["patient_name"] = None
            ctx["doctor"] = None
            ctx["time"] = None
            ctx["day"] = None
            ctx["available_doctors"] = None
            ctx["available_slots"] = None
            ctx["appointments"] = None
            ctx["selected_appointment"] = None
            ctx["rescheduling"] = False
            ctx["area"] = None

            return {"reply": "Would you like to book an appointment? (yes/no)"}
        
        elif msg == "2":
            ctx["mode"] = "reschedule"
            ctx["awaiting"] = "reschedule_name"
            return {"reply": "Please enter your name to reschedule your appointment."}

        # =================================================
        # ❌ LEGACY CANCEL FLOW (COMMENTED — DO NOT DELETE)
        # =================================================
        # elif msg == "3":
        #     ctx["mode"] = "cancel"
        #     ctx["awaiting"] = "patient_name_lookup"
        #     return {"reply": "Please enter your name to cancel appointment."}

        # =================================================
        # ✅ MODIFICATION: USER-SCOPED CANCEL FLOW
        # =================================================
        elif msg == "3":

            appointments = get_user_active_appointments(user_id)

            if not appointments:
                return {"reply": "You have no active appointments to cancel."}

            ctx["mode"] = "cancel"
            ctx["awaiting"] = "cancel_select"
            ctx["appointments"] = appointments

            reply = "Please select the appointment you want to cancel:\n\n"
            for i, a in enumerate(appointments, 1):
                reply += f"{i}. {a['doctor']} | {a['date']} | {a['time']}\n"

            return {"reply": reply}

        return {"reply": "Please choose 1, 2, or 3."}
    

    # =================================================
    # BOOKING CONSENT
    # =================================================
    if ctx["awaiting"] == "booking_consent":

        if msg in ("yes", "y"):
            ctx["awaiting"] = "area"
            return {"reply": "Please tell me your area of residence."}

        if msg in ("no", "n"):
            booking_context.pop(user_id, None)
            return {"reply": "Okay. Take care."}

        return {"reply": "Please reply with yes or no."}
    
      # =================================================
    # AREA HANDLER
    # =================================================
    # =================================================
    # AREA HANDLER — NORMALIZATION FIX (CRITICAL)
    # =================================================
    if ctx["awaiting"] == "area":

        # 🔧 FIX: normalize area ONCE
        ctx["area"] = msg.strip().lower().replace(" ", "_")

        catalog_reply = get_doctor_catalog(ctx["area"], ctx["specialty"])


        if catalog_reply.get("type") == "fallback_offer":
            ctx["fallback_specialty"] = catalog_reply["fallback_specialty"]
            ctx["awaiting"] = "fallback_consent"
            return {
                "reply": (
                    f"No {ctx['specialty']} found in {ctx['area'].title()}.\n"
                    f"Consult {ctx['fallback_specialty']} instead? (yes/no)"
                )
            }

        ctx["available_doctors"] = catalog_reply["doctors"]
        ctx["awaiting"] = "doctor_selection"
        return {
            "reply": (
                "🩺 Available Doctors:\n\n"
                f"{format_doctor_list(ctx['available_doctors'])}\n"
                "Please choose a doctor by number."
            )
        }

    # =================================================
    # 🔁 FALLBACK CONSENT HANDLER (CRITICAL FIX)
    # =================================================
    if ctx["awaiting"] == "fallback_consent":
        if msg not in ("yes", "no"):
            return {"reply": "Please answer yes or no."}

        if msg == "no":
            booking_context.pop(user_id, None)
            return {"reply": "Okay, booking cancelled."}

        ctx["specialty"] = ctx["fallback_specialty"]
        ctx["awaiting"] = "doctor_selection"

        catalog_reply = get_doctor_catalog(ctx["area"], ctx["specialty"])
        doctors = catalog_reply.get("doctors", [])

        if not doctors:
            booking_context.pop(user_id, None)
            return {"reply": "No doctors available. Please try later."}

        ctx["available_doctors"] = doctors

        return {
            "reply": (
                f"🩺 Available {ctx['specialty']} doctors:\n\n"
                f"{format_doctor_list(doctors)}\n"
                "Please choose a doctor number."
            )
        }

    # =================================================
    # DOCTOR SELECTION
    # =================================================
    if ctx["awaiting"] == "doctor_selection":
        if not msg.isdigit():
            return {"reply": "Please choose a valid doctor number."}
        try:
            ctx["doctor"] = ctx["available_doctors"][int(msg) - 1]
        except IndexError:
            return {"reply": "Invalid doctor selection."}
        ctx["awaiting"] = "day_selection"
        return {"reply": f"You selected {ctx['doctor']['name']}. Please choose a day."}

    # =================================================
    # DAY SELECTION
    # =================================================
    if ctx["awaiting"] == "day_selection":
        day = msg.title()
        slots = ctx["doctor"]["schedule"].get(day)
        if not slots:
            return {"reply": "Please choose a valid day from the schedule."}

        booked = get_unavailable_slots(ctx["doctor"]["name"], day)
        ctx["available_slots"] = [s for s in slots if s not in booked]

        if not ctx["available_slots"]:
            return {"reply": f"No available slots on {day}. Choose another day."}

        ctx["day"] = day
        ctx["awaiting"] = "time_selection"
        return {
            "reply": (
                f"Available slots on {day}:\n\n"
                f"{', '.join(ctx['available_slots'])}\n\n"
                "Please choose a time slot."
            )
        }

    # =================================================
    # TIME SELECTION
    # =================================================
    if ctx["awaiting"] == "time_selection":
        user_time = msg.replace(" ", "")
        normalized = [s.replace(" ", "") for s in ctx["available_slots"]]
        if user_time not in normalized:
            return {"reply": "Please choose a valid available time slot."}

        ctx["time"] = ctx["available_slots"][normalized.index(user_time)]
        ctx["awaiting"] = "name"
        return {"reply": "Please enter patient name."}
    
        # =================================================
    # FINAL BOOKING
    # =================================================
    # if ctx["awaiting"] == "name":
    #     ctx["patient_name"] = msg.title()
    #     _, reply = book_appointment_with_user(user_id, {
    #         "patient_name": ctx["patient_name"],
    #         "doctor": ctx["doctor"]["name"],
    #         "date": ctx["day"],
    #         "time": ctx["time"]
    #     })
    #     booking_context.pop(user_id, None)
    #     return {"reply": reply}

    # =================================================
    # BOOKING PREVIEW (NEW)
    # =================================================
    if ctx["awaiting"] == "name":
        ctx["patient_name"] = msg.title()

        preview = (
            "Please confirm your appointment:\n\n"
            f"Doctor: {ctx['doctor']['name']} ({ctx['doctor']['specialty'].title()})\n"
            # f"Area: {ctx['doctor']['area']}\n"
            f"Area: {ctx['area'].replace('_', ' ').title()}\n"
            f"Day: {ctx['day']}\n"
            f"Time: {ctx['time']}\n"
            f"Patient: {ctx['patient_name']}\n\n"
            "Confirm? (yes / no)"
        )

        ctx["awaiting"] = "confirm_booking"
        return {"reply": preview}
    
    # =================================================
    # BOOKING CONFIRMATION (FINAL COMMIT)
    # =================================================
    if ctx["awaiting"] == "confirm_booking":

        if msg == "no":
            booking_context.pop(user_id, None)
            return {"reply": "❌ Booking cancelled. Let me know if you want to start again."}

        if msg != "yes":
            return {"reply": 'Please reply with "yes" or "no".'}

        _, reply = book_appointment_with_user(user_id, {
            "patient_name": ctx["patient_name"],
            "doctor": ctx["doctor"]["name"],
            "date": ctx["day"],
            "time": ctx["time"]
        })

        booking_context.pop(user_id, None)
        return {"reply": reply}



    # =================================================
    # ✅ MODIFICATION: CANCEL — SELECT APPOINTMENT
    # =================================================
    if ctx["awaiting"] == "cancel_select":

        if not msg.isdigit():
            return {"reply": "Please enter a valid appointment number."}

        index = int(msg) - 1

        try:
            selected = ctx["appointments"][index]
        except IndexError:
            return {"reply": "Invalid selection. Please try again."}

        ctx["selected_appointment"] = selected
        ctx["awaiting"] = "cancel_confirm"

        return {
            "reply": (
                "Are you sure you want to cancel this appointment?\n\n"
                f"Doctor: {selected['doctor']}\n"
                f"Date: {selected['date']}\n"
                f"Time: {selected['time']}\n\n"
                "Reply with yes or no."
            )
        }

    # =================================================
    # ✅ MODIFICATION: CANCEL — CONFIRMATION (FINAL FIX)
    # =================================================
    if ctx["awaiting"] == "cancel_confirm":

        if msg.lower() == "no":
            booking_context.pop(user_id, None)
            return {"reply": "Cancellation aborted."}

        if msg.lower() != "yes":
            return {"reply": "Please reply with yes or no."}

        appt = ctx["selected_appointment"]

        cancel_appointment_db(
            appointment_id=appt["id"],
            user_id=user_id
        )

        booking_context.pop(user_id, None)
        return {"reply": "✅ Appointment cancelled successfully."}

    # =================================================
    # BOOKING / RESCHEDULE LOGIC (UNCHANGED, BELOW)
    # =================================================

    print("UNHANDLED STATE:", ctx["awaiting"], "msg =", msg)
    return {"reply": "Something went wrong. Please try again."}
