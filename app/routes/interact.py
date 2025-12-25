# from fastapi import APIRouter, Request
# from pydantic import BaseModel
# import re

# from services.booking_service import (
#     book_appointment_with_user,
#     get_unavailable_slots,
# )

# from services.profile_service import (
#     get_user_active_appointments,
#     cancel_appointment_db
# )

# from utils.emergency_support import (
#     detect_emergency_level,
#     infer_specialty_from_symptoms,
#     format_sos_message,
#     format_home_care
# )

# from services.catalog_service import get_doctor_catalog

# router = APIRouter()
# booking_context = {}


# class ChatRequest(BaseModel):
#     message: str


# SPECIALTY_MAP = {
#     "cardiology": "cardiologist",
#     "neurology": "neurologist",
#     "gastroenterology": "gastroenterologist",
#     "general": "general_physician",
# }


# def format_doctor_list(doctors):
#     out = ""
#     for i, d in enumerate(doctors, 1):
#         days = ", ".join(d["schedule"].keys())
#         out += f"{i}. {d['name']} ({days})\n"
#     return out

# def format_appointments_list(appts):
#     response = ""
#     for i, a in enumerate(appts, start=1):
#         response += f"{i}. {a[1]} — {a[2]} — {a[3]}\n"
#     return response


# @router.post("/interact")
# def interact(req: ChatRequest, request: Request):

#     user = request.session.get("user")
#     if not user:
#         return {"reply": "❌ Please log in to continue."}

#     user_id = user["id"]
#     msg = re.sub(r"\s+", " ", re.sub(r"[.,]", "", req.message.lower().strip()))

#     if user_id not in booking_context:
#         booking_context[user_id] = {
#             "awaiting": None,
#             "pending_confirmation": None,
#             "patient_name": None,
#             "doctor": None,
#             "day": None,
#             "time": None,
#             "available_doctors": [],
#             "available_slots": [],
#             "appointments": [],
#             "selected_appointment": None,
#             "specialty": None,
#             "fallback_specialty": None,
#             "area": None,
#             "emergency_checked": False,
#         }

#     ctx = booking_context[user_id]

#     # ================= TRIAGE =================
#     if not ctx["emergency_checked"] and ctx["awaiting"] is None:
#         ctx["emergency_checked"] = True
#         ctx["specialty"] = SPECIALTY_MAP.get(
#             infer_specialty_from_symptoms(msg),
#             infer_specialty_from_symptoms(msg)
#         )

#         if detect_emergency_level(msg) == "HIGH":
#             return {"reply": format_sos_message()}

#         ctx["awaiting"] = "action_selection"
#         return {"reply": f"{format_home_care()}\n\n1️⃣ Book\n2️⃣ Reschedule\n3️⃣ Cancel"}

#     # ================= ACTION =================
#     if ctx["awaiting"] == "action_selection":
#         if msg == "1":
#             ctx["awaiting"] = "booking_consent"
#             return {"reply": "Do you want to book an appointment? (yes/no)"}

#         if msg == "3":
#             appts = get_user_active_appointments(user_id)
#             if not appts:
#                 return {"reply": "You have no active appointments."}
#             ctx["appointments"] = appts
#             ctx["awaiting"] = "cancel_select"
#             text = "Select appointment to cancel:\n"
#             for i, a in enumerate(appts, 1):
#                 text += f"{i}. {a['doctor']} | {a['date']} | {a['time']}\n"
#             return {"reply": text}

#         return {"reply": "Choose 1, 2 or 3."}

#     # ================= BOOKING CONSENT =================
#     if ctx["awaiting"] == "booking_consent":
#         if msg == "yes":
#             ctx["awaiting"] = "area"
#             return {"reply": "Enter your area."}
#         booking_context.pop(user_id, None)
#         return {"reply": "Cancelled."}

#     # ================= AREA =================
#     if ctx["awaiting"] == "area":
#         ctx["area"] = msg.replace(" ", "_")
#         reply = get_doctor_catalog(ctx["area"], ctx["specialty"])

#         if reply.get("type") == "fallback_offer":
#             ctx["fallback_specialty"] = reply["fallback_specialty"]
#             ctx["awaiting"] = "fallback_consent"
#             return {"reply": f"No {ctx['specialty']} found. Use {ctx['fallback_specialty']}? (yes/no)"}

#         ctx["available_doctors"] = reply["doctors"]

#         if len(ctx["available_doctors"]) == 1:
#             ctx["doctor"] = ctx["available_doctors"][0]
#             ctx["pending_confirmation"] = "doctor"
#             ctx["awaiting"] = "confirm_single"
#             return {"reply": f"Only one doctor: {ctx['doctor']['name']}. Continue? (yes/no)"}

#         ctx["awaiting"] = "doctor_selection"
#         return {"reply": "Doctors:\n" + format_doctor_list(ctx["available_doctors"])}

#     # ================= FALLBACK =================
#     if ctx["awaiting"] == "fallback_consent":
#         if msg != "yes":
#             booking_context.pop(user_id, None)
#             return {"reply": "Cancelled."}
#         ctx["specialty"] = ctx["fallback_specialty"]
#         ctx["awaiting"] = "area"
#         return {"reply": "Rechecking doctors..."}

#     # ================= CONFIRM SINGLE =================
#     if ctx["awaiting"] == "confirm_single":
#         if msg != "yes":
#             booking_context.pop(user_id, None)
#             return {"reply": "Cancelled."}

#         step = ctx["pending_confirmation"]
#         ctx["pending_confirmation"] = None

#         if step == "doctor":
#             ctx["awaiting"] = "day_selection"
#             return {"reply": "Enter day."}

#         if step == "day":
#             ctx["awaiting"] = "time_selection"
#             return {"reply": f"Available slots:\n{', '.join(ctx['available_slots'])}"}

#         if step == "time":
#             ctx["awaiting"] = "name"
#             return {"reply": "Enter patient name."}

#     # ================= DOCTOR =================
#     if ctx["awaiting"] == "doctor_selection":
#         i = int(msg) - 1
#         ctx["doctor"] = ctx["available_doctors"][i]
#         ctx["awaiting"] = "day_selection"
#         return {"reply": "Enter day."}

#     # ================= DAY =================
#     if ctx["awaiting"] == "day_selection":
#         day = msg.title()
#         slots = ctx["doctor"]["schedule"].get(day)
#         if not slots:
#             return {"reply": "Invalid day."}
#         booked = get_unavailable_slots(ctx["doctor"]["name"], day)
#         ctx["available_slots"] = [s for s in slots if s not in booked]
#         ctx["day"] = day

#         if len(ctx["available_slots"]) == 1:
#             ctx["time"] = ctx["available_slots"][0]
#             ctx["pending_confirmation"] = "time"
#             ctx["awaiting"] = "confirm_single"
#             return {"reply": f"Only one slot {ctx['time']}. Continue? (yes/no)"}

#         ctx["awaiting"] = "time_selection"
#         return {"reply": f"Choose time:\n{', '.join(ctx['available_slots'])}"}

#     # ================= TIME =================
#     if ctx["awaiting"] == "time_selection":
#         if msg not in [s.replace(" ", "") for s in ctx["available_slots"]]:
#             return {"reply": "Invalid time."}
#         ctx["time"] = ctx["available_slots"][0]
#         ctx["awaiting"] = "name"
#         return {"reply": "Enter patient name."}

#     # ================= FINAL =================
#     if ctx["awaiting"] == "name":
#         _, reply = book_appointment_with_user(user_id, {
#             "patient_name": msg.title(),
#             "doctor": ctx["doctor"]["name"],
#             "date": ctx["day"],
#             "time": ctx["time"]
#         })
#         booking_context.pop(user_id, None)
#         return {"reply": reply}

#     return {"reply": "Something went wrong."}












from fastapi import APIRouter, Request
from pydantic import BaseModel
import re

from services.booking_service import (
    book_appointment_with_user,
    get_unavailable_slots,
)

from services.profile_service import (
    get_user_active_appointments,
    cancel_appointment_db
)

from utils.emergency_support import (
    detect_emergency_level,
    infer_specialty_from_symptoms,
    format_sos_message,
    format_home_care
)

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


def format_doctor_list(doctors, show_index=True):
    text = ""
    for i, d in enumerate(doctors, 1):
        specialty = d.get("specialty", "").replace("_", " ").title()

        if show_index:
            text += f"{i}. {d['name']} ({specialty})\n"
        else:
            text += f"{d['name']} ({specialty})\n"

    return text


@router.post("/interact")
def interact(req: ChatRequest, request: Request):

    user = request.session.get("user")
    if not user:
        return {"reply": "❌ Please log in to continue."}

    user_id = user["id"]
    msg = re.sub(r"\s+", " ", re.sub(r"[.,]", "", req.message.lower().strip()))

    if user_id not in booking_context:
        booking_context[user_id] = {
            "awaiting": None,
            "pending_confirmation": None,
            "patient_name": None,
            "doctor": None,
            "day": None,
            "time": None,
            "available_doctors": [],
            "available_days": [],
            "available_slots": [],
            "appointments": [],
            "selected_appointment": None,
            "specialty": None,
            "fallback_specialty": None,
            "area": None,
            "emergency_checked": False,
        }

    ctx = booking_context[user_id]

    # ================= TRIAGE =================
    if not ctx["emergency_checked"] and ctx["awaiting"] is None:
        ctx["emergency_checked"] = True
        ctx["specialty"] = SPECIALTY_MAP.get(
            infer_specialty_from_symptoms(msg),
            infer_specialty_from_symptoms(msg)
        )

        if detect_emergency_level(msg) == "HIGH":
            return {"reply": format_sos_message()}

        ctx["awaiting"] = "action_selection"
        return {
            "reply": (
                f"{format_home_care()}\n\n"
                "1️⃣ Book appointment\n"
                "2️⃣ Reschedule\n"
                "3️⃣ Cancel"
            )
        }

    # ================= ACTION =================
    if ctx["awaiting"] == "action_selection":
        if msg == "1":
            ctx["awaiting"] = "booking_consent"
            return {"reply": "Do you want to book an appointment? (yes/no)"}

        if msg == "3":
            appts = get_user_active_appointments(user_id)
            if not appts:
                return {"reply": "You have no active appointments."}
            ctx["appointments"] = appts
            ctx["awaiting"] = "cancel_select"
            reply = "Select appointment to cancel:\n\n"
            for i, a in enumerate(appts, 1):
                reply += f"{i}. {a['doctor']} | {a['date']} | {a['time']}\n"
            return {"reply": reply}

        return {"reply": "Please choose 1, 2 or 3."}

    # ================= BOOKING CONSENT =================
    if ctx["awaiting"] == "booking_consent":
        if msg == "yes":
            ctx["awaiting"] = "area"
            return {"reply": "Enter your area."}
        booking_context.pop(user_id, None)
        return {"reply": "Booking cancelled."}

    # ================= AREA =================
    if ctx["awaiting"] == "area":
        ctx["area"] = msg.replace(" ", "_")
        catalog = get_doctor_catalog(ctx["area"], ctx["specialty"])

        if catalog.get("type") == "fallback_offer":
            ctx["fallback_specialty"] = catalog["fallback_specialty"]
            ctx["awaiting"] = "fallback_consent"
            return {
                "reply": (
                    f"No {ctx['specialty']} found.\n"
                    f"Consult {ctx['fallback_specialty']} instead? (yes/no)"
                )
            }

        ctx["available_doctors"] = catalog["doctors"]

        doctor_list = format_doctor_list(ctx["available_doctors"])

        if len(ctx["available_doctors"]) == 1:
            ctx["doctor"] = ctx["available_doctors"][0]
            ctx["pending_confirmation"] = "doctor"
            ctx["awaiting"] = "confirm_single"
            doctor_list = format_doctor_list(
                ctx["available_doctors"],
                show_index=False
            )

            return {
                "reply": (
                    "Available doctor:\n\n"
                    f"{doctor_list}\n"
                    "Only one doctor is available. Continue? (yes/no)"
                )
            }
        
        doctor_list = format_doctor_list(
            ctx["available_doctors"],
            show_index=True
        )

        ctx["awaiting"] = "doctor_selection"
        return {"reply": "Available doctors:\n\n" + doctor_list}

    # ================= FALLBACK =================
    if ctx["awaiting"] == "fallback_consent":
        if msg != "yes":
            booking_context.pop(user_id, None)
            return {"reply": "Booking cancelled."}
        ctx["specialty"] = ctx["fallback_specialty"]
        ctx["awaiting"] = "area"
        return {"reply": "Rechecking doctors..."}

    # ================= CONFIRM SINGLE =================
    if ctx["awaiting"] == "confirm_single":
        if msg != "yes":
            booking_context.pop(user_id, None)
            return {"reply": "Booking cancelled."}

        step = ctx["pending_confirmation"]
        ctx["pending_confirmation"] = None

        if step == "doctor":
            ctx["available_days"] = list(ctx["doctor"]["schedule"].keys())
            ctx["awaiting"] = "day_catalog"

        elif step == "day":
            ctx["awaiting"] = "time_catalog"

        elif step == "time":
            ctx["awaiting"] = "name"
            return {"reply": "Please enter patient name."}


    # ================= DOCTOR SELECTION =================
    if ctx["awaiting"] == "doctor_selection":
        try:
            ctx["doctor"] = ctx["available_doctors"][int(msg) - 1]
        except:
            return {"reply": "Invalid doctor selection."}

        ctx["available_days"] = list(ctx["doctor"]["schedule"].keys())
        ctx["awaiting"] = "day_catalog"

    # ================= DAY CATALOG =================
    if ctx["awaiting"] == "day_catalog":
        days = "\n".join(f"- {d}" for d in ctx["available_days"])

        if len(ctx["available_days"]) == 1:
            ctx["day"] = ctx["available_days"][0]
            ctx["pending_confirmation"] = "day"
            ctx["awaiting"] = "confirm_single"
            return {
                "reply": (
                    "Available day:\n\n"
                    f"{days}\n\n"
                    "Only one day is available. Continue? (yes/no)"
                )
            }

        ctx["awaiting"] = "day_selection"
        return {
            "reply": (
                "Available days:\n\n"
                f"{days}\n\n"
                "Please choose a day."
            )
        }

    # ================= DAY SELECTION =================
    if ctx["awaiting"] == "day_selection":
        day = msg.title()
        if day not in ctx["doctor"]["schedule"]:
            return {"reply": "Please choose a day from the list."}

        slots = ctx["doctor"]["schedule"][day]
        booked = get_unavailable_slots(ctx["doctor"]["name"], day)
        ctx["available_slots"] = [s for s in slots if s not in booked]
        ctx["day"] = day
        ctx["awaiting"] = "time_catalog"

    # ================= TIME CATALOG =================
    if ctx["awaiting"] == "time_catalog":
        slots_text = "\n".join(f"- {s}" for s in ctx["available_slots"])

        if len(ctx["available_slots"]) == 1:
            ctx["time"] = ctx["available_slots"][0]
            ctx["pending_confirmation"] = "time"
            ctx["awaiting"] = "confirm_single"
            return {
                "reply": (
                    "Available time slot:\n\n"
                    f"{slots_text}\n\n"
                    "Only one slot is available. Continue? (yes/no)"
                )
            }

        ctx["awaiting"] = "time_selection"
        return {
            "reply": (
                "Available time slots:\n\n"
                f"{slots_text}\n\n"
                "Please choose a time."
            )
        }

    # ================= TIME SELECTION =================
    if ctx["awaiting"] == "time_selection":
        normalized = [s.replace(" ", "") for s in ctx["available_slots"]]

        if msg not in normalized:
            return {"reply": "Please choose a time from the list."}

        ctx["time"] = ctx["available_slots"][normalized.index(msg)]
        ctx["awaiting"] = "name"
    # ================= FINAL =================
    if ctx["awaiting"] == "name":
        _, reply = book_appointment_with_user(user_id, {
            "patient_name": msg.title(),
            "doctor": ctx["doctor"]["name"],
            "date": ctx["day"],
            "time": ctx["time"]
        })

        doctor_name = ctx["doctor"]["name"]
        doctor_specialty = ctx["doctor"]["specialty"].title()
        area = ctx["area"].replace("_", " ").title()
        day = ctx["day"]

        why_text = (
        f"I suggested {doctor_name} because your symptoms matched "
        f"{doctor_specialty.lower()}, they practice near {area}, "
        f"and have availability on {day}."
    )

        booking_context.pop(user_id, None)
        final_reply = (
        f"{reply}\n\n"
        f"ℹ️ Why this doctor?\n"
        f"{why_text}"
    )

    booking_context.pop(user_id, None)
    return {"reply": final_reply}




    return {"reply": "Something went wrong."}
