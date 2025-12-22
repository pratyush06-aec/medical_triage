from fastapi import APIRouter, Request
from services.booking_service import (
    book_appointment,
    get_appointments,
    get_appointments_by_patient,
    delete_appointment,
)

# =================================================
# ✅ ROUTER (REQUIRED)
# =================================================
router = APIRouter(prefix="/booking", tags=["Booking"])


# =================================================
# 📅 BOOK APPOINTMENT
# =================================================
@router.post("/book")
def book(data: dict, request: Request):
    user_id = request.session.get("user_id")
    success, message = book_appointment(data)
    return {"success": success, "message": message}


# =================================================
# 📋 LIST ALL APPOINTMENTS (LEGACY)
# =================================================
@router.get("/all")
def list_all():
    return get_appointments()


# =================================================
# 👤 APPOINTMENTS BY PATIENT NAME (LEGACY)
# =================================================
@router.get("/patient/{patient_name}")
def list_by_patient(patient_name: str):
    return get_appointments_by_patient(patient_name)


# =================================================
# ❌ CANCEL APPOINTMENT
# =================================================
@router.post("/cancel/{appointment_id}")
def cancel(appointment_id: int, request: Request):
    user_id = request.session.get("user_id")
    ok = delete_appointment(appointment_id, user_id)
    return {"success": ok}
