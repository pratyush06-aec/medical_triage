from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from services.auth_service import register, login
from services.profile_service import get_user_appointment_summary

router = APIRouter(prefix="/auth")


class AuthRequest(BaseModel):
    email: str
    password: str


# =================================================
# REGISTER
# =================================================
@router.post("/register")
def register_user(req: AuthRequest, request: Request):
    user = register(req.email, req.password)

    if not user:
        return {"error": "User already exists"}

    # ❌ OLD (WRONG SESSION SHAPE — DO NOT DELETE)
    # request.session["user_id"] = user[0]

    # ✅ FIX: unified session schema used everywhere else
    request.session["user"] = {
        "id": user[0],
        "email": req.email
    }

    return {"message": "Registered successfully"}


# =================================================
# LOGIN
# =================================================
@router.post("/login")
def login_user(req: AuthRequest, request: Request):
    user_id = login(req.email, req.password)

    if not user_id:
        return {"error": "Invalid credentials"}

    # ❌ OLD (INCOMPATIBLE WITH interact.py / profile.py)
    # request.session["user_id"] = user_id

    # ✅ FIX: unified session schema
    request.session["user"] = {
        "id": user_id,
        "email": req.email
    }

    return {"message": "Logged in successfully"}


# =================================================
# LOGOUT
# =================================================
@router.post("/logout")
def logout_user(request: Request):
    request.session.clear()
    return {"message": "Logged out"}


# =================================================
# PROFILE APPOINTMENTS (AUTH-GUARDED)
# =================================================
@router.get("/profile/appointments")
def profile_appointments(request: Request):
    user = request.session.get("user")

    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    summary = get_user_appointment_summary(user["id"])
    return summary
