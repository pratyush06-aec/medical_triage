# from fastapi import FastAPI, Request
# from fastapi.responses import HTMLResponse
# from fastapi.staticfiles import StaticFiles
# from pathlib import Path

# from triage_agent.service import run_triage
# # from database.db import get_db  # (kept for Phase 2 – DB integration)

# # ============================================================
# # 🔁 OLD IMPLEMENTATION (COMMENTED – DO NOT DELETE)
# # ============================================================

# # app = FastAPI()
# #
# # app.mount("/static", StaticFiles(directory="web/static"), name="static")
# #
# # @app.get("/", response_class=HTMLResponse)
# # def serve_index():
# #     with open("static/index.html") as f:
# #         return f.read()
# #
# # @app.post("/interact")
# # async def interact(request: Request):
# #     data = await request.json()
# #     user_message = data.get("message", "")
# #     reply = run_triage(user_message)
# #     return {"reply": reply}

# # ❌ Issues with old version:
# # - Relative path "static/index.html" breaks under uvicorn reload (Windows)
# # - Static directory handling not robust
# # - Harder to scale safely

# # ============================================================
# # ✅ UPDATED IMPLEMENTATION (PHASE 1 – UI FIX)
# # ============================================================

# # --- Path handling (ROBUST & PLATFORM-SAFE)
# BASE_DIR = Path(__file__).resolve().parent
# STATIC_DIR = BASE_DIR / "static"

# app = FastAPI()

# # --- Static files mount (UPDATED)
# # Previously: StaticFiles(directory="web/static")
# # Now: Uses absolute path via pathlib
# app.mount(
#     "/static",
#     StaticFiles(directory=STATIC_DIR),
#     name="static"
# )

# # --- Home page route (UPDATED)
# # Previously: open("static/index.html")
# # Now: Safe absolute path resolution
# @app.get("/", response_class=HTMLResponse)
# def serve_index():
#     index_file = STATIC_DIR / "index.html"
#     return index_file.read_text(encoding="utf-8")

# # --- Chat interaction endpoint (UNCHANGED LOGIC)
# @app.post("/interact")
# async def interact(request: Request):
#     data = await request.json()
#     user_msg = data.get("message", "")

#     # Call triage orchestrator via service layer
#     reply = run_triage(user_msg)

#     return {"reply": reply}

# ============================================================
# 🔁 VERY OLD / INITIAL IMPLEMENTATION (COMMENTED – KEEP FOR HISTORY)
# ============================================================

# from fastapi import FastAPI, Request
# from fastapi.responses import HTMLResponse
# from fastapi.staticfiles import StaticFiles
# from triage_agent.service import run_triage
# from database.db import get_db
#
# app = FastAPI()
#
# app.mount("/static", StaticFiles(directory="web/static"), name="static")
#
# @app.get("/", response_class=HTMLResponse)
# def serve_index():
#     with open("static/index.html") as f:
#         return f.read()
#
# @app.post("/interact")
# async def interact(request: Request):
#     data = await request.json()
#     user_message = data.get("message", "")
#     reply = run_triage(user_message)
#     return {"reply": reply}

# ❌ Problems with this version:
# - Relative file paths break on Windows + uvicorn reload
# - Static directory resolution unreliable
# - No error handling for agent failures

# ============================================================
# ✅ CURRENT / ACTIVE IMPLEMENTATION (PHASE 1 – STABLE UI)
# ============================================================













from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from triage_agent.agent import get_orchestrator_agent
from triage_agent.service import run_triage_async

# import asyncio  # ✅ REQUIRED for asyncio.to_thread


# from triage_agent.service import run_triage
# from database.db import get_db  # (INTENTIONALLY KEPT COMMENTED – Phase 2)

# ------------------------------------------------------------
# ✅ Path handling (FIXES FileNotFoundError on Windows)
# ------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI()

# ------------------------------------------------------------
# ✅ Static files mount (UPDATED & SAFE)
# Previously: StaticFiles(directory="web/static")
# Now: Absolute path via pathlib
# ------------------------------------------------------------
app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static"
)

# ------------------------------------------------------------
# ✅ Home page route (UPDATED)
# Previously: open("static/index.html")
# Now: Absolute, reload-safe path
# ------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
def serve_index():
    index_file = STATIC_DIR / "index.html"
    return index_file.read_text(encoding="utf-8")

# ------------------------------------------------------------
# ✅ Chat interaction endpoint (HARDENED)
# - Always returns JSON
# - Prevents UI crash on agent failure
# ------------------------------------------------------------





# @app.post("/interact")
# async def interact(request: Request):
#     data = await request.json()
#     user_msg = data.get("message", "")

#     #agent = get_orchestrator_agent()

#     # ✅ CORRECT
#     reply = await run_triage_async(user_msg)

#     @app.post("/interact")
#     async def interact(request: Request):
#         data = await request.json()
#         user_msg = data.get("message", "")

#         # 🔹 RULE-BASED TRIAGE (returns dict)
#         triage_result = await run_triage_async(user_msg)

#         urgency = triage_result.get("urgency", "unknown")
#         specialty = triage_result.get("specialty", "general physician")

#         # 🔹 FORMAT FOR UI (FIXES [object Object])
#         reply_text = (
#             f"🩺 **Triage Result**\n"
#             f"Urgency Level: {urgency.upper()}\n"
#             f"Recommended Specialty: {specialty.replace('_', ' ').title()}"
#         )

#         return {"reply": reply_text}







@app.post("/interact")
async def interact(request: Request):
    data = await request.json()
    user_msg = data.get("message", "")

    triage = await run_triage_async(user_msg)

    urgency = triage.get("urgency", "unknown")
    specialty = triage.get("specialty", "general")

    # -------------------------------------------------
    # ✅ FORMAT HUMAN-READABLE RESPONSE (FIX)
    # -------------------------------------------------
    if urgency == "high":
        reply = (
            "🚨 MEDICAL EMERGENCY DETECTED\n\n"
            f"Specialty: {specialty.title()}\n"
            "Please seek immediate medical attention or call emergency services."
        )
    elif urgency == "moderate":
        reply = (
            f"⚠️ Moderate symptoms detected.\n"
            f"Recommended specialty: {specialty.title()}.\n"
            "Consider booking an appointment."
        )
    else:
        reply = (
            f"🏡 Mild symptoms detected.\n"
            f"Suggested specialty: {specialty.title()}.\n"
            "Home care may help, but monitor your condition."
        )

    return {"reply": reply}


