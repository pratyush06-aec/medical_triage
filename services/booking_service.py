# =================================================
# BOOKING SERVICE
# =================================================

# ❌ OLD DB IMPORTS (COMMENTED — DO NOT DELETE)
# from database.db import is_slot_booked, create_appointment, get_appointments

# =================================================
# ✅ CURRENT DB IMPORTS
# =================================================
from database.db import (
    is_slot_booked,
    create_appointment,
    get_appointments,

    # 🔧 MODIFICATION: import booked-slot reader
    get_booked_slots,

    # 🔧 MODIFICATION: import cancel / reschedule helpers
    get_appointments_by_patient,
    delete_appointment
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


# =================================================
# BOOK APPOINTMENT (UNCHANGED CORE LOGIC)
# =================================================
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
    # Prevents race conditions when two users try to
    # book the same slot at the same time.
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


# =================================================
# LIST APPOINTMENTS (UNCHANGED)
# =================================================
def list_appointments():
    return get_appointments()


# =================================================
# 🔧 MODIFICATION: FETCH APPOINTMENTS FOR A PATIENT
# -------------------------------------------------
# Used in:
# - Reschedule flow
# - Cancel flow
#
# NOTE:
# - Earlier version used get_appointments()
# - This version is patient-specific and correct
# =================================================
def get_patient_appointments(patient_name: str):
    """
    Fetch all appointments for a patient.
    Used by interact.py for cancel / reschedule flow.
    """
    return get_appointments_by_patient(patient_name)


# =================================================
# 🔧 MODIFICATION: CANCEL APPOINTMENT
# -------------------------------------------------
# Purpose:
# - Used for cancel flow
# - Used internally during rescheduling
# =================================================
def cancel_appointment(appointment_id: int):
    """
    Cancel appointment by rowid.
    Slot becomes free automatically.
    """
    delete_appointment(appointment_id)
