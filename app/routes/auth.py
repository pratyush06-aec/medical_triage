# from fastapi import APIRouter, Request, HTTPException
# from pydantic import BaseModel
# from services.auth_service import register, login
# from services.profile_service import get_user_appointment_summary

# router = APIRouter(prefix="/auth")


# class AuthRequest(BaseModel):
#     email: str
#     password: str


# # =================================================
# # REGISTER
# # =================================================
# @router.post("/register")
# def register_user(req: AuthRequest, request: Request):
#     user = register(req.email, req.password)

#     if not user:
#         return {"error": "User already exists"}

#     # ❌ OLD (WRONG SESSION SHAPE — DO NOT DELETE)
#     # request.session["user_id"] = user[0]

#     # ✅ FIX: unified session schema used everywhere else
#     request.session["user"] = {
#         "id": user[0],
#         "email": req.email
#     }

#     return {"message": "Registered successfully"}


# # =================================================
# # LOGIN
# # =================================================
# @router.post("/login")
# def login_user(req: AuthRequest, request: Request):
#     user_id = login(req.email, req.password)

#     if not user_id:
#         return {"error": "Invalid credentials"}

#     # ❌ OLD (INCOMPATIBLE WITH interact.py / profile.py)
#     # request.session["user_id"] = user_id

#     # ✅ FIX: unified session schema
#     request.session["user"] = {
#         "id": user_id,
#         "email": req.email
#     }

#     return {"message": "Logged in successfully"}


# # =================================================
# # LOGOUT
# # =================================================
# @router.post("/logout")
# def logout_user(request: Request):
#     request.session.clear()
#     return {"message": "Logged out"}


# # =================================================
# # PROFILE APPOINTMENTS (AUTH-GUARDED)
# # =================================================
# @router.get("/profile/appointments")
# def profile_appointments(request: Request):
#     user = request.session.get("user")

#     if not user:
#         raise HTTPException(status_code=401, detail="Not authenticated")

#     summary = get_user_appointment_summary(user["id"])
#     return summary















from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from services.auth_service import register, login
from services.profile_service import get_user_appointment_summary

router = APIRouter(prefix="/auth", tags=["auth"])


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

    # ❌ OLD (WRONG SESSION STORAGE — DO NOT DELETE)
    # Used session["user_id"], which is NOT used anywhere else
    #
    # request.session["user_id"] = user[0]

    # =================================================
    # ✅ STEP 2 — VERIFIED SESSION STORAGE KEY
    # =================================================
    # Auth state is stored ONLY here:
    # request.session["user"]
    #
    # /auth/me, /profile, /interact ALL read from this key
    request.session["user"] = {
        "id": user[0],
        "email": req.email
    }

    return {"ok": True}  # 🔧 normalized response


# =================================================
# LOGIN
# =================================================

# ❌ OLD LOGIN IMPLEMENTATION (COMMENTED — DO NOT DELETE)
# This version caused reload loops and inconsistent UI state
#
# @router.post("/login")
# def login_user(req: AuthRequest, request: Request):
#     user_id = login(req.email, req.password)
#
#     if not user_id:
#         return {"error": "Invalid credentials"}
#
#     request.session["user"] = {
#         "id": user_id,
#         "email": req.email
#     }
#
#     return {"message": "Logged in successfully"}


# ❌ INCORRECT LOGIN IMPLEMENTATION (COMMENTED — DO NOT DELETE)
# Backend redirect does NOT work with fetch()
#
# from fastapi.responses import RedirectResponse
#
# @router.post("/login")
# def login_user(req: AuthRequest, request: Request):
#     user_id = login(req.email, req.password)
#
#     if not user_id:
#         return {"error": "Invalid credentials"}
#
#     request.session["user"] = {
#         "id": user_id,
#         "email": req.email
#     }
#
#     return RedirectResponse("/", status_code=303)


# =================================================
# ✅ FINAL LOGIN IMPLEMENTATION (SESSION VERIFIED)
# =================================================
@router.post("/login")
def login_user(req: AuthRequest, request: Request):
    user_id = login(req.email, req.password)

    if not user_id:
        return {"error": "Invalid credentials"}

    # =================================================
    # ✅ STEP 2 — VERIFIED SESSION STORAGE KEY
    # =================================================
    # This is the ONLY place login stores auth state
    request.session["user"] = {
        "id": user_id,
        "email": req.email
    }

    return {"ok": True}


# =================================================
# LOGOUT
# =================================================

# ❌ OLD LOGOUT IMPLEMENTATION (COMMENTED — DO NOT DELETE)
#
# @router.post("/logout")
# def logout_user(request: Request):
#     request.session.clear()
#     return {"message": "Logged out"}


# ✅ CURRENT LOGOUT (CORRECT)
@router.post("/logout")
async def logout_user(request: Request):
    request.session.clear()
    return {"ok": True}


# =================================================
# ❌ OLD /auth/me IMPLEMENTATION (COMMENTED — DO NOT DELETE)
# ❌ INVALID because this project DOES NOT use session["user_id"]
#
# @router.get("/me")
# def get_current_user(request: Request):
#     user_id = request.session.get("user_id")
#
#     if not user_id:
#         raise HTTPException(status_code=401, detail="Not authenticated")
#
#     return {"user_id": user_id}


# =================================================
# ✅ FINAL /auth/me — STEP 2 VERIFIED
# =================================================
@router.get("/me")
def get_current_user(request: Request):
    """
    🔐 Authoritative auth check

    STEP 2 VERIFICATION:
    - Reads ONLY from request.session["user"]
    - This must match how login stores auth state
    """

    user = request.session.get("user")

    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    return {
        "id": user["id"],
        "email": user["email"]
    }


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
