from fastapi import APIRouter, Request
from services.profile_service import get_profile
from services.booking_service import cancel_appointment

router = APIRouter(prefix="/profile")

@router.get("/me")
def my_profile(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        return {"error": "Not authenticated"}
    return get_profile(user_id)


@router.post("/cancel/{appointment_id}")
def cancel(appointment_id: int, request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        return {"error": "Not authenticated"}
    return cancel_appointment(user_id, appointment_id)
