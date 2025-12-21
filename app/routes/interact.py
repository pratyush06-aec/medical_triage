from fastapi import APIRouter, Request
from pydantic import BaseModel
import re

# =================================================
# 🔧 MODIFICATION: IMPORT CANCEL / LOOKUP HELPERS
# =================================================
from services.booking_service import (
    book_appointment,
    get_unavailable_slots,
    get_patient_appointments,
    cancel_appointment
)

# =================================================
# TRIAGE + SPECIALTY INFERENCE (UNCHANGED)
# =================================================
from utils.emergency_support import (
    detect_emergency_level,
    infer_specialty_from_symptoms,
    format_sos_message,
    format_home_care
)

# =================================================
# CATALOG SERVICE (UNCHANGED)
# =================================================
from services.catalog_service import get_doctor_catalog

router = APIRouter()
booking_context = {}


class ChatRequest(BaseModel):
    message: str


# =================================================
# 🔧 FORMAT DOCTOR LIST FOR UI
# =================================================
def format_doctor_list(doctors):
    response = ""
    for i, doc in enumerate(doctors, start=1):
        days = ", ".join(doc["schedule"].keys())
        response += f"{i}. {doc['name']} ({days})\n"
    return response


# =================================================
# 🔧 FORMAT APPOINTMENTS LIST
# =================================================
def format_appointments_list(appts):
    response = ""
    for i, a in enumerate(appts, start=1):
        response += f"{i}. {a[1]} — {a[2]} — {a[3]}\n"
    return response


@router.post("/interact")
def interact(req: ChatRequest, request: Request):
    user_id = request.client.host
    msg = req.message.lower().strip()
    msg = re.sub(r"[.,]", "", msg)
    msg = re.sub(r"\s+", " ", msg)

    # =================================================
    # 🔧 CONTEXT INITIALIZATION (FSM-SAFE)
    # =================================================
    if user_id not in booking_context:
        booking_context[user_id] = {

            # ---------------------------
            # BASIC BOOKING DATA
            # ---------------------------
            "patient_name": None,
            "doctor": None,
            "time": None,
            "day": None,
            "awaiting": None,
            "available_doctors": None,
            "available_slots": None,

            # ---------------------------
            # MODE
            # ---------------------------
            "mode": None,  # book | reschedule | cancel

            # ---------------------------
            # RESCHEDULE / CANCEL DATA
            # ---------------------------
            "appointments": None,
            "selected_appointment": None,
            "rescheduling": False,

            # ---------------------------
            # TRIAGE DATA
            # ---------------------------
            "emergency_checked": False,
            "emergency_level": None,
            "specialty": None,
            "fallback_specialty": None,
            "area": None,
            "symptom_text": None
        }

    ctx = booking_context[user_id]

    # =================================================
    # TRIAGE (RUNS ONLY ONCE)
    # =================================================
    if not ctx["emergency_checked"] and ctx["awaiting"] is None:
        ctx["symptom_text"] = msg
        ctx["emergency_level"] = detect_emergency_level(msg)
        ctx["specialty"] = infer_specialty_from_symptoms(msg)
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
            ctx["mode"] = "book"
            ctx["awaiting"] = "booking_consent"
            return {"reply": "Would you like to book an appointment? (yes/no)"}

        elif msg == "2":
            ctx["mode"] = "reschedule"
            ctx["awaiting"] = "reschedule_name"
            return {"reply": "Please enter your name to reschedule your appointment."}

        elif msg == "3":
            ctx["mode"] = "cancel"
            ctx["awaiting"] = "patient_name_lookup"
            return {"reply": "Please enter your name to cancel appointment."}

        return {"reply": "Please choose 1, 2, or 3."}

    # =================================================
    # BOOKING CONSENT HANDLER
    # =================================================
    if ctx["awaiting"] == "booking_consent":
        if msg in ["yes", "y"]:
            ctx["awaiting"] = "area"
            return {"reply": "Please tell me your area of residence."}

        booking_context.pop(user_id, None)
        return {"reply": "Okay. Take care."}

    # =================================================
    # AREA HANDLER (RESTORED FROM OLD FILE)
    # =================================================
    if ctx["awaiting"] == "area":
        ctx["area"] = msg.lower()
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
    # DOCTOR SELECTION (RESTORED)
    # =================================================
    if ctx["awaiting"] == "doctor_selection":
        if not msg.isdigit():
            return {"reply": "Please choose a valid doctor number."}

        index = int(msg) - 1
        try:
            ctx["doctor"] = ctx["available_doctors"][index]
        except IndexError:
            return {"reply": "Invalid doctor selection."}

        ctx["awaiting"] = "day_selection"
        return {
            "reply": (
                f"You selected {ctx['doctor']['name']}.\n"
                "Please choose a day."
            )
        }

    # =================================================
    # DAY SELECTION (RESTORED)
    # =================================================
    if ctx["awaiting"] == "day_selection":
        day = msg.title()
        slots = ctx["doctor"]["schedule"].get(day)

        if not slots:
            return {"reply": "Please choose a valid day from the schedule."}

        booked = get_unavailable_slots(ctx["doctor"]["name"], day)
        ctx["available_slots"] = [s for s in slots if s not in booked]

        if not ctx["available_slots"]:
            return {"reply": f"No available slots on {day}. Please choose another day."}

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
    # TIME SELECTION (RESTORED)
    # =================================================
    if ctx["awaiting"] == "time_selection":
        user_time = msg.replace(" ", "")
        slots = ctx["available_slots"]
        normalized = [s.replace(" ", "") for s in slots]

        if user_time not in normalized:
            return {"reply": "Please choose a valid available time slot."}

        ctx["time"] = slots[normalized.index(user_time)]
        ctx["awaiting"] = "name"
        return {"reply": "Please enter patient name."}

    # =================================================
    # FINAL BOOKING STEP (RESTORED)
    # =================================================
    if ctx["awaiting"] == "name":
        ctx["patient_name"] = msg.title()

        success, message = book_appointment({
            "patient_name": ctx["patient_name"],
            "doctor": ctx["doctor"]["name"],
            "date": ctx["day"],
            "time": ctx["time"]
        })

        booking_context.pop(user_id, None)
        return {"reply": message}

    # =================================================
    # RESCHEDULE NAME HANDLER (NEW FILE KEPT)
    # =================================================
    if ctx["awaiting"] == "reschedule_name":
        ctx["patient_name"] = msg.title()
        appts = get_patient_appointments(ctx["patient_name"])

        if not appts:
            booking_context.pop(user_id, None)
            return {"reply": "❌ No appointments found under this name."}

        ctx["appointments"] = appts
        ctx["awaiting"] = "reschedule_select_appointment"

        return {
            "reply": (
                "📋 Your Appointments:\n\n"
                f"{format_appointments_list(appts)}\n"
                "Please choose which appointment you want to reschedule."
            )
        }

    # =================================================
    # 🔧 RESCHEDULE APPOINTMENT SELECTION (SAFE)
    # =================================================
    if ctx["awaiting"] == "reschedule_select_appointment":

        if not msg.isdigit():
            return {"reply": "Please choose a valid appointment number."}

        index = int(msg) - 1
        try:
            selected = ctx["appointments"][index]
        except IndexError:
            return {"reply": "Invalid selection."}

        ctx["selected_appointment"] = selected
        doctor_name = selected[1]

        # =================================================
        # ❌ OLD (UNSAFE LOOKUP — COMMENTED, DO NOT DELETE)
        # =================================================
        # catalog = get_doctor_catalog("", "")
        # ctx["doctor"] = next(
        #     d for d in catalog
        #     if d["name"] == doctor_name
        # )

        # =================================================
        # ✅ FIX: get_doctor_catalog returns a LIST here
        #      Safe lookup with defensive handling
        # =================================================
        catalog = get_doctor_catalog("", "")

        try:
            ctx["doctor"] = next(
                d for d in catalog
                if d["name"] == doctor_name
            )
        except StopIteration:
            # Defensive safety — prevents 500 server crash
            booking_context.pop(user_id, None)
            return {
                "reply": "❌ Doctor record not found. Please contact support."
            }

        ctx["rescheduling"] = True
        ctx["awaiting"] = "reschedule_day"

        return {
            "reply": (
                f"You are rescheduling appointment with {doctor_name}.\n\n"
                "Available days:\n"
                f"{', '.join(ctx['doctor']['schedule'].keys())}\n\n"
                "Please choose a day."
            )
        }

    # =================================================
    # RESCHEDULE DAY
    # =================================================
    if ctx["awaiting"] == "reschedule_day":

        day = msg.title()
        slots = ctx["doctor"]["schedule"].get(day)

        if not slots:
            return {"reply": "Please choose a valid day from the doctor's schedule."}

        booked = get_unavailable_slots(ctx["doctor"]["name"], day)
        ctx["available_slots"] = [s for s in slots if s not in booked]

        if not ctx["available_slots"]:
            return {"reply": f"No available slots on {day}. Choose another day."}

        ctx["day"] = day
        ctx["awaiting"] = "reschedule_time"

        return {
            "reply": (
                f"Available slots on {day}:\n\n"
                f"{', '.join(ctx['available_slots'])}\n\n"
                "Please choose a time."
            )
        }

    # =================================================
    # RESCHEDULE FINAL STEP
    # =================================================
    if ctx["awaiting"] == "reschedule_time":

        user_time = msg.replace(" ", "")
        slots = ctx["available_slots"]
        normalized = [s.replace(" ", "") for s in slots]

        if user_time not in normalized:
            return {"reply": "Please choose a valid available time slot."}

        ctx["time"] = slots[normalized.index(user_time)]

        cancel_appointment(ctx["selected_appointment"][0])

        book_appointment({
            "patient_name": ctx["patient_name"],
            "doctor": ctx["doctor"]["name"],
            "date": ctx["day"],
            "time": ctx["time"]
        })

        booking_context.pop(user_id, None)
        return {"reply": "✅ Appointment rescheduled successfully."}

    # =================================================
    # CANCEL FLOW (RESTORED)
    # =================================================
    if ctx["awaiting"] == "patient_name_lookup":
        ctx["patient_name"] = msg.title()
        appts = get_patient_appointments(ctx["patient_name"])

        if not appts:
            booking_context.pop(user_id, None)
            return {"reply": "❌ No appointments found under this name."}

        ctx["appointments"] = appts
        ctx["awaiting"] = "appointment_selection"

        return {
            "reply": (
                "📋 Your Appointments:\n\n"
                f"{format_appointments_list(appts)}\n"
                "Choose appointment number."
            )
        }

    if ctx["awaiting"] == "appointment_selection":
        index = int(msg) - 1
        try:
            selected = ctx["appointments"][index]
        except (ValueError, IndexError):
            return {"reply": "Invalid selection."}

        cancel_appointment(selected[0])
        booking_context.pop(user_id, None)
        return {"reply": "✅ Your appointment has been cancelled."}

    # =================================================
    # SAFETY NET — MUST REMAIN
    # =================================================
    print("UNHANDLED STATE:", ctx["awaiting"], "msg =", msg)
    return {"reply": "Something went wrong. Please try again."}
