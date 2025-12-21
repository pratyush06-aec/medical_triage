from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from database.db import init_db
from app.routes import booking, interact   # 👈 ADD THIS

app = FastAPI(title="Medical Triage System")

init_db()

# API routes
app.include_router(booking.router)
app.include_router(interact.router)        # 👈 ADD THIS

# ---- UI ----
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "web" / "static"

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
def serve_ui():
    return FileResponse(STATIC_DIR / "index.html")
