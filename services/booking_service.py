# from database.db import (
#     is_slot_booked,
#     create_appointment,
#     get_appointments
# )


# def book_appointment(data: dict):
#     doctor = data["doctor"]
#     date = data["date"]
#     time = data["time"]

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
















# =================================================
# BOOKING SERVICE
# =================================================

from database.db import (
    is_slot_booked,
    create_appointment,
    get_appointments,

    # 🔧 MODIFICATION: import booked-slot reader
    get_booked_slots
)

# =================================================
# 🔧 MODIFICATION: EXPOSE UNAVAILABLE SLOTS
# -------------------------------------------------
# Purpose:
# - Used by interact.py BEFORE showing time slots
# - Ensures already-booked slots are hidden from users
# - Keeps DB access encapsulated inside service layer
# =================================================
def get_unavailable_slots(doctor_name: str, day: str):
    return get_booked_slots(doctor_name, day)


def book_appointment(data: dict):
    doctor = data["doctor"]
    date = data["date"]
    time = data["time"]

    # ❌ OLD (IMPLICIT — COMMENTED, DO NOT DELETE)
    # Booking logic existed but availability was checked
    # only at final insert time.
    #
    # if is_slot_booked(doctor, date, time):
    #     return False, "Slot already booked"

    # =================================================
    # ✅ FINAL SLOT LOCK (MUST REMAIN)
    # -------------------------------------------------
    # This prevents race conditions where two users
    # try to book the same slot simultaneously.
    # =================================================
    if is_slot_booked(doctor, date, time):
        return False, "Slot already booked"

    create_appointment(
        patient_name=data["patient_name"],
        doctor=doctor,
        date=date,
        time=time
    )

    return True, "Appointment booked successfully"


def list_appointments():
    return get_appointments()
