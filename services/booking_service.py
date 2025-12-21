# # =================================================
# # BOOKING SERVICE
# # =================================================

# from database.db import (
#     is_slot_booked,
#     create_appointment,
#     get_appointments,

#     # 🔧 MODIFICATION: import booked-slot reader
#     get_booked_slots
# )

# # =================================================
# # 🔧 MODIFICATION: EXPOSE UNAVAILABLE SLOTS
# # -------------------------------------------------
# # Purpose:
# # - Used by interact.py BEFORE showing time slots
# # - Ensures already-booked slots are hidden from users
# # - Keeps DB access encapsulated inside service layer
# # =================================================
# def get_unavailable_slots(doctor_name: str, day: str):
#     return get_booked_slots(doctor_name, day)


# def book_appointment(data: dict):
#     doctor = data["doctor"]
#     date = data["date"]
#     time = data["time"]

#     # ❌ OLD (IMPLICIT — COMMENTED, DO NOT DELETE)
#     # Booking logic existed but availability was checked
#     # only at final insert time.
#     #
#     # if is_slot_booked(doctor, date, time):
#     #     return False, "Slot already booked"

#     # =================================================
#     # ✅ FINAL SLOT LOCK (MUST REMAIN)
#     # -------------------------------------------------
#     # This prevents race conditions where two users
#     # try to book the same slot simultaneously.
#     # =================================================
#     if is_slot_booked(doctor, date, time):
#         return False, "Slot already booked"

#     create_appointment(
#         patient_name=data["patient_name"],
#         doctor=doctor,
#         date=date,
#         time=time
#     )

#     return True, "Appointment booked successfully"


# def list_appointments():
#     return get_appointments()










from database.db import (
    create_appointment,
    is_slot_booked,
    get_booked_slots,
    cancel_appointment_db
)

# =================================================
# ❌ OLD BOOKING (COMMENTED — DO NOT DELETE)
# =================================================
# def book_appointment(data: dict):
#     ...

# =================================================
# ✅ USER-AWARE BOOKING (NEW)
# =================================================
def book_appointment_with_user(user_id: int, data: dict):
    doctor = data["doctor"]
    date = data["date"]
    time = data["time"]

    if is_slot_booked(doctor, date, time):
        return False, "Slot already booked"

    create_appointment(
        patient_name=data["patient_name"],
        doctor=doctor,
        date=date,
        time=time,
        user_id=user_id
    )

    return True, "✅ Appointment booked successfully"


def cancel_appointment(user_id: int, appointment_id: int):
    success = cancel_appointment_db(appointment_id, user_id)
    if not success:
        return False, "Unable to cancel appointment"
    return True, "❌ Appointment cancelled successfully"

# =================================================
# 🔁 COMPATIBILITY WRAPPER (DO NOT DELETE)
# -------------------------------------------------
# Purpose:
# - Keeps existing imports working
# - Routes legacy calls to new user-aware logic
# - Uses user_id = None for now
# =================================================
def book_appointment(data: dict):
    # ❗ TEMPORARY fallback for old callers
    # This will be fully removed once interact.py
    # is fully session-based
    return book_appointment_with_user(
        user_id=None,
        data=data
    )

# =================================================
# 🔁 LEGACY COMPATIBILITY (DO NOT DELETE)
# -------------------------------------------------
# Purpose:
# - Keeps old booking routes working
# - Prevents import crashes
# - Will be removed after full migration
# =================================================
from database.db import get_appointments

def list_appointments():
    return get_appointments()

# =================================================
# 🔁 LEGACY SLOT VISIBILITY HELPER (DO NOT DELETE)
# -------------------------------------------------
# Purpose:
# - Used by interact.py to hide booked slots
# - Delegates to DB layer
# =================================================
from database.db import get_booked_slots

def get_unavailable_slots(doctor_name: str, day: str):
    return get_booked_slots(doctor_name, day)
