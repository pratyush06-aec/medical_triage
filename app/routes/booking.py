# from fastapi import APIRouter, Request
# from services.booking_service import (
#     book_appointment,
#     get_appointments,
#     get_appointments_by_patient,
#     delete_appointment,
# )
# from services.booking_service import book_appointment_with_user

# # =================================================
# # ✅ ROUTER (REQUIRED)
# # =================================================
# router = APIRouter(prefix="/booking", tags=["Booking"])


# # =================================================
# # 📅 BOOK APPOINTMENT
# # =================================================

# @router.post("/book")
# def book(data: dict, request: Request):
#     user = request.session.get("user")
#     user_id = user["id"] if user else None

#     if not user_id:
#         return {"success": False, "message": "Not authenticated"}

#     success, message = book_appointment_with_user(user_id, data)
#     return {"success": success, "message": message}

# # =================================================
# # 📋 LIST ALL APPOINTMENTS (LEGACY)
# # =================================================
# @router.get("/all")
# def list_all():
#     return get_appointments()


# # =================================================
# # 👤 APPOINTMENTS BY PATIENT NAME (LEGACY)
# # =================================================
# @router.get("/patient/{patient_name}")
# def list_by_patient(patient_name: str):
#     return get_appointments_by_patient(patient_name)


# # =================================================
# # ❌ CANCEL APPOINTMENT
# # =================================================
# @router.post("/cancel/{appointment_id}")
# def cancel(appointment_id: int, request: Request):
#     user_id = request.session.get("user_id")
#     ok = delete_appointment(appointment_id, user_id)
#     return {"success": ok}














# from fastapi import APIRouter, Request, HTTPException
# from services.booking_service import (
#     book_appointment,
#     get_appointments,
#     get_appointments_by_patient,
#     delete_appointment,
# )
# from services.booking_service import book_appointment_with_user

# # =================================================
# # ✅ ROUTER (REQUIRED)
# # =================================================
# router = APIRouter(prefix="/booking", tags=["Booking"])


# # =================================================
# # 📅 BOOK APPOINTMENT
# # =================================================
# @router.post("/book")
# def book(data: dict, request: Request):
#     user = request.session.get("user")
#     user_id = user["id"] if user else None

#     if not user_id:
#         return {"success": False, "message": "Not authenticated"}

#     success, message = book_appointment_with_user(user_id, data)
#     return {"success": success, "message": message}


# # =================================================
# # 📋 LIST ALL APPOINTMENTS (LEGACY)
# # =================================================
# @router.get("/all")
# def list_all():
#     return get_appointments()


# # =================================================
# # 👤 APPOINTMENTS BY PATIENT NAME (LEGACY)
# # =================================================
# @router.get("/patient/{patient_name}")
# def list_by_patient(patient_name: str):
#     return get_appointments_by_patient(patient_name)


# # =================================================
# # ❌ CANCEL APPOINTMENT
# # =================================================
# @router.post("/cancel/{appointment_id}")
# def cancel(appointment_id: int, request: Request):

#     # =================================================
#     # ❌ OLD LOGIC (COMMENTED — DO NOT DELETE)
#     # -------------------------------------------------
#     # user_id = request.session.get("user_id")
#     # ok = delete_appointment(appointment_id, user_id)
#     # return {"success": ok}
#     # =================================================


#     # =================================================
#     # ✅ MODIFICATION STARTS HERE
#     # -------------------------------------------------

#     # ✅ Validate appointment ID
#     if appointment_id <= 0:
#         raise HTTPException(
#             status_code=400,
#             detail="Invalid appointment ID"
#         )

#     # ✅ Correct session access
#     user = request.session.get("user")
#     user_id = user["id"] if user else None

#     if not user_id:
#         raise HTTPException(
#             status_code=401,
#             detail="Not authenticated"
#         )

#     ok = delete_appointment(appointment_id, user_id)
#     return {"success": ok}

#     # =================================================
#     # ✅ MODIFICATION ENDS HERE
#     # =================================================














from fastapi import APIRouter, Request, HTTPException
from services.booking_service import (
    book_appointment,
    get_appointments,
    get_appointments_by_patient,
    delete_appointment,
)
from services.booking_service import book_appointment_with_user

# =================================================
# ✅ ROUTER (REQUIRED)
# =================================================
router = APIRouter(prefix="/booking", tags=["Booking"])


# =================================================
# 📅 BOOK APPOINTMENT
# =================================================
@router.post("/book")
def book(data: dict, request: Request):
    user = request.session.get("user")
    user_id = user["id"] if user else None

    if not user_id:
        return {"success": False, "message": "Not authenticated"}

    success, message = book_appointment_with_user(user_id, data)
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

    # =================================================
    # ❌ OLD LOGIC (COMMENTED — DO NOT DELETE)
    # -------------------------------------------------
    # user_id = request.session.get("user_id")
    # ok = delete_appointment(appointment_id, user_id)
    # return {"success": ok}
    # =================================================


    # =================================================
    # ✅ MODIFICATION STARTS HERE
    # -------------------------------------------------

    # 1️⃣ Validate appointment ID
    if appointment_id <= 0:
        raise HTTPException(
            status_code=400,
            detail="Invalid appointment ID"
        )

    # 2️⃣ Correct session access (user object, not user_id)
    user = request.session.get("user")
    user_id = user["id"] if user else None

    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated"
        )

    # 3️⃣ Cancel appointment with ownership enforcement
    ok = delete_appointment(appointment_id, user_id)

    return {"success": ok}

    # =================================================
    # ✅ MODIFICATION ENDS HERE
    # =================================================

