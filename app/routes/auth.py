from fastapi import APIRouter, Request
from pydantic import BaseModel
from services.auth_service import register, login

router = APIRouter(prefix="/auth")

class AuthRequest(BaseModel):
    email: str
    password: str


@router.post("/register")
def register_user(req: AuthRequest, request: Request):
    user = register(req.email, req.password)
    if not user:
        return {"error": "User already exists"}
    request.session["user_id"] = user[0]
    return {"message": "Registered successfully"}


@router.post("/login")
def login_user(req: AuthRequest, request: Request):
    user_id = login(req.email, req.password)
    if not user_id:
        return {"error": "Invalid credentials"}
    request.session["user_id"] = user_id
    return {"message": "Logged in successfully"}


# =================================================
# ✅ LOGOUT (NEW)
# =================================================
@router.post("/logout")
def logout_user(request: Request):
    request.session.clear()
    return {"message": "Logged out"}
