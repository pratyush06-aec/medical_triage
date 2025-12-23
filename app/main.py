# from fastapi import FastAPI
# from fastapi.staticfiles import StaticFiles
# from fastapi.responses import FileResponse
# from pathlib import Path
# from starlette.middleware.sessions import SessionMiddleware

# from database.db import init_db
# from app.routes import booking, interact
# from app.routes.auth import router as auth_router
# from app.routes.profile import router as profile_router

# app = FastAPI(title="Medical Triage System")

# app.add_middleware(SessionMiddleware, secret_key="dev-secret")

# init_db()

# app.include_router(booking.router)
# app.include_router(interact.router)
# app.include_router(auth_router)
# app.include_router(profile_router)

# BASE_DIR = Path(__file__).resolve().parent.parent
# STATIC_DIR = BASE_DIR / "web" / "static"

# app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# @app.get("/")
# def serve_ui():
#     return FileResponse(STATIC_DIR / "index.html")















# from fastapi import FastAPI, Request
# from fastapi.staticfiles import StaticFiles
# from fastapi.responses import FileResponse, RedirectResponse
# from fastapi.templating import Jinja2Templates
# from pathlib import Path
# from starlette.middleware.sessions import SessionMiddleware

# from database.db import init_db
# from app.routes import booking, interact
# from app.routes.auth import router as auth_router
# from app.routes.profile import router as profile_router

# # =====================================================
# # APP INITIALIZATION
# # =====================================================
# app = FastAPI(title="Medical Triage System")

# # Session middleware (already correct)
# app.add_middleware(SessionMiddleware, secret_key="dev-secret")

# # Initialize database
# init_db()

# # =====================================================
# # ROUTERS
# # =====================================================
# app.include_router(booking.router)
# app.include_router(interact.router)
# app.include_router(auth_router)
# app.include_router(profile_router)

# # =====================================================
# # STATIC FILES
# # =====================================================
# BASE_DIR = Path(__file__).resolve().parent.parent
# STATIC_DIR = BASE_DIR / "web" / "static"

# app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# # =====================================================
# # TEMPLATES
# # =====================================================
# # 🔧 MODIFICATION:
# # Using Jinja2Templates to serve auth-guarded HTML pages
# templates = Jinja2Templates(directory="web/templates")

# # =====================================================
# # ROOT ROUTE "/" — AUTH GUARDED (MODIFIED EARLIER)
# # =====================================================
# @app.get("/")
# async def home(request: Request):
#     """
#     🔐 HARD AUTH GUARD
#     - If user is NOT logged in → redirect to /login
#     - If logged in → serve index.html
#     """

#     # 🔧 MODIFICATION: Added session-based auth guard
#     if not request.session.get("user"):
#         return RedirectResponse("/login", status_code=302)

#     # 🔧 MODIFICATION: Serve index.html via templates
#     return templates.TemplateResponse(
#         "index.html",
#         {"request": request}
#     )

# # =====================================================
# # OLD ROOT ROUTE (COMMENTED — DO NOT DELETE)
# # =====================================================
# # ❌ OLD BEHAVIOR:
# # This served index.html directly WITHOUT auth check
# #
# # @app.get("/")
# # def serve_ui():
# #     return FileResponse(STATIC_DIR / "index.html")

# # =====================================================
# # LOGIN PAGE ROUTE "/login" — AUTH-AWARE (NEW MODIFICATION)
# # =====================================================
# @app.get("/login")
# async def login_page(request: Request):
#     """
#     🔐 LOGIN PAGE RULE
#     - If user IS logged in → redirect to /
#     - If NOT logged in → show auth.html
#     """

#     # 🔧 MODIFICATION: Prevent logged-in users from seeing login page
#     if request.session.get("user"):
#         return RedirectResponse("/", status_code=302)

#     # 🔧 MODIFICATION: Serve auth.html via templates
#     return templates.TemplateResponse(
#         "auth.html",
#         {"request": request}
#     )

# # =====================================================
# # OLD LOGIN SERVING LOGIC (COMMENTED — IF IT EXISTED)
# # =====================================================
# # ❌ OLD BEHAVIOR (example):
# # This would serve auth.html without session awareness
# #
# # @app.get("/login")
# # def serve_login():
# #     return FileResponse(STATIC_DIR / "auth.html")
# (STATIC_DIR / "index.html")















from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from starlette.middleware.sessions import SessionMiddleware

from database.db import init_db
from app.routes import booking, interact
from app.routes.auth import router as auth_router
from app.routes.profile import router as profile_router

# =====================================================
# APP INITIALIZATION
# =====================================================
app = FastAPI(title="Medical Triage System")

# =====================================================
# SESSION MIDDLEWARE
# =====================================================

# ❌ OLD SESSION MIDDLEWARE (COMMENTED — DO NOT DELETE)
# This version caused session to not persist correctly
#
# app.add_middleware(SessionMiddleware, secret_key="dev-secret")

# ✅ MODIFICATION:
# Explicit session configuration
# - same_site="lax" allows redirects after login
# - https_only=False for local development
# - ❌ DO NOT set max_age (prevents instant expiry)
app.add_middleware(
    SessionMiddleware,
    secret_key="dev-secret",
    same_site="lax",
    https_only=False
)

# =====================================================
# INITIALIZE DATABASE
# =====================================================
init_db()

# =====================================================
# ROUTERS
# =====================================================
app.include_router(booking.router)
app.include_router(interact.router)
app.include_router(auth_router)
app.include_router(profile_router)

# =====================================================
# STATIC FILES
# =====================================================
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "web" / "static"

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# =====================================================
# TEMPLATES
# =====================================================
# 🔧 MODIFICATION:
# Using Jinja2Templates to serve auth-guarded HTML pages
templates = Jinja2Templates(directory="web/templates")

# =====================================================
# ROOT ROUTE "/" — AUTH GUARDED
# =====================================================
@app.get("/")
async def home(request: Request):
    """
    🔐 HARD AUTH GUARD
    - If user is NOT logged in → redirect to /login
    - If logged in → serve index.html
    """

    if not request.session.get("user"):
        return RedirectResponse("/login", status_code=302)

    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )

# =====================================================
# OLD ROOT ROUTE (COMMENTED — DO NOT DELETE)
# =====================================================
# ❌ OLD BEHAVIOR:
# Served index.html directly WITHOUT auth check
#
# @app.get("/")
# def serve_ui():
#     return FileResponse(STATIC_DIR / "index.html")

# =====================================================
# LOGIN PAGE ROUTE "/login" — AUTH-AWARE
# =====================================================
@app.get("/login")
async def login_page(request: Request):
    """
    🔐 LOGIN PAGE RULE
    - If user IS logged in → redirect to /
    - If NOT logged in → show auth.html
    """

    if request.session.get("user"):
        return RedirectResponse("/", status_code=302)

    return templates.TemplateResponse(
        "auth.html",
        {"request": request}
    )

# =====================================================
# OLD LOGIN SERVING LOGIC (COMMENTED — DO NOT DELETE)
# =====================================================
# ❌ OLD BEHAVIOR:
# Served auth.html without session awareness
#
# @app.get("/login")
# def serve_login():
#     return FileResponse(STATIC_DIR / "auth.html")

# =====================================================
# ❌ STRAY DEBUG LINE (COMMENTED — CAUSED 500 ERROR)
# =====================================================
# (STATIC_DIR / "index.html")
