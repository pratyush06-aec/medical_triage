from fastapi import APIRouter, Request, HTTPException
from services.profile_service import get_user_appointment_summary

router = APIRouter()

@router.get("/profile/appointments")
def profile_appointments(request: Request):
    user_id = request.session.get("user_id")

    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    return get_user_appointment_summary(user_id)
