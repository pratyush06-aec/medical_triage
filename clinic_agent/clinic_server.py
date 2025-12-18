from typing import List, Dict, Optional
import datetime
import zoneinfo
import re
import os
import asyncio, logging

# load .env if present

from dotenv import load_dotenv
load_dotenv()

# ADK imports (A2A)
from google.adk.agents import LlmAgent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.models.google_llm import Gemini
from google.genai import types

from triage_agent.agent import get_orchestrator_agent


# ============================================================
# ADDED: Initialize triage orchestrator ONCE (required by A2A)
# ============================================================

orchestrator_agent = get_orchestrator_agent()



# ------------------------------------------------------------------
# model + retry config (same as triage agent)
MODEL_NAME = "gemini-2.5-flash-lite"
retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)

# timezone for date -> weekday conversion (used by availability helpers)
KOLKATA_TZ = zoneinfo.ZoneInfo("Asia/Kolkata")

def _normalize(text: Optional[str]) -> str:
    return (text or "").strip().lower()

def _weekday_from_input(day_or_date: Optional[str]) -> Optional[str]:
    if not day_or_date:
        return None
    s = day_or_date.strip()
    s_lower = s.lower()
    weekdays_long = {
        "mon": "monday", "monday": "monday",
        "tue": "tuesday", "tues": "tuesday", "tuesday": "tuesday",
        "wed": "wednesday", "wednesday": "wednesday",
        "thu": "thursday", "thur": "thursday", "thursday": "thursday",
        "fri": "friday", "friday": "friday",
        "sat": "saturday", "saturday": "saturday",
        "sun": "sunday", "sunday": "sunday",
    }
    if s_lower in weekdays_long:
        return weekdays_long[s_lower]
    date_match = re.match(r"^(\d{4})[-/](\d{1,2})[-/](\d{1,2})$", s)
    if date_match:
        y, m, d = map(int, date_match.groups())
        try:
            dt = datetime.datetime(y, m, d, tzinfo=KOLKATA_TZ)
            return dt.strftime("%A").lower()
        except Exception:
            return None
    return None

# -------------------------
# Example doctors dataset (extend as needed)
# -------------------------
_DOCTORS: Dict[str, Dict] = {
    "d1": {
        "doctor_id": "d1",
        "name": "Dr. Anita Singh",
        "specialty": "general_physician",
        "availability": {"monday": ["downtown"], "wednesday": ["dankuni"], "thursday": ["belur", "dankuni"]},
    },
    "d2": {
        "doctor_id": "d2",
        "name": "Dr. Raj Patel",
        "specialty": "general_physician",
        "availability": {"tuesday": ["downtown"], "thursday": ["belur"]},
    },
    "d3": {
        "doctor_id": "d3",
        "name": "Dr. Meera Rao",
        "specialty": "cardiology",
        "availability": {"thursday": ["dankuni"], "friday": ["uptown"]},
    },
    "d4": {
        "doctor_id": "d4",
        "name": "Dr. X ENT",
        "specialty": "ent",
        "availability": {"wednesday": ["dankuni"], "thursday": ["belur"]},
    },
}

_CLINICS: Dict[str, Dict] = {
    "c1": {"clinic_id": "c1", "name": "Downtown Health Clinic", "area": "downtown"},
    "c2": {"clinic_id": "c2", "name": "Downtown Urgent Care", "area": "downtown"},
    "c3": {"clinic_id": "c3", "name": "Uptown Family Clinic", "area": "uptown"},
    "c4": {"clinic_id": "c4", "name": "Dankuni ENT Center", "area": "dankuni"},
    "c5": {"clinic_id": "c5", "name": "Belur Medical Center", "area": "belur"},
}

def _doctor_available_in_area_on_weekday(doctor: Dict, area: Optional[str], weekday: Optional[str]) -> bool:
    if weekday:
        avail = doctor.get("availability", {})
        day_list = avail.get(weekday, [])
        if not area:
            return bool(day_list)
        return _normalize(area) in [a.lower() for a in day_list]
    if area:
        for areas in doctor.get("availability", {}).values():
            if _normalize(area) in [a.lower() for a in areas]:
                return True
        return False
    return True

# -------------------------
# Tools exposed by this agent
# -------------------------
def get_clinic_info(area: str) -> dict:
    area_norm = _normalize(area)
    clinics = [c for c in _CLINICS.values() if _normalize(c["area"]) == area_norm]
    return {"clinics": clinics}

def get_doctors(specialty: str, area: Optional[str] = None, day: Optional[str] = None) -> list:
    spec_norm = _normalize(specialty)
    weekday = _weekday_from_input(day)
    results = []
    for doc in _DOCTORS.values():
        if _normalize(doc.get("specialty")) != spec_norm:
            continue
        if _doctor_available_in_area_on_weekday(doc, area, weekday):
            results.append(
                {
                    "doctor_id": doc["doctor_id"],
                    "name": doc["name"],
                    "specialty": doc["specialty"],
                    "availability": doc.get("availability", {}),
                }
            )
    return results

def get_doctor_availability(doctor_id: str, date_or_day: Optional[str] = None) -> dict:
    did = _normalize(doctor_id)
    doc = _DOCTORS.get(did) or next((d for d in _DOCTORS.values() if _normalize(d["doctor_id"]) == did), None)
    if not doc:
        return {"error": f"Doctor '{doctor_id}' not found."}
    if date_or_day:
        weekday = _weekday_from_input(date_or_day)
        if not weekday:
            return {"error": f"Could not parse date or weekday from '{date_or_day}'. Use YYYY-MM-DD or weekday name."}
        areas = doc.get("availability", {}).get(weekday, [])
        return {"doctor_id": doc["doctor_id"], "available": bool(areas), "weekday": weekday, "areas": areas}
    return {"doctor_id": doc["doctor_id"], "name": doc["name"], "weekly_availability": doc.get("availability", {})}

# -------------------------
# Create the A2A LlmAgent and expose it
# -------------------------
clinic_agent = LlmAgent(
    model=Gemini(model=MODEL_NAME, retry_options=retry_config),
    name="clinic_directory_agent",
    description="Clinic directory agent providing clinic & doctor info.",
    instruction=(
        "You provide clinic and doctor information. Use the provided tools to look up clinics and doctors, "
        "and return structured results when asked."
    ),
    tools=[get_clinic_info, get_doctors, get_doctor_availability],
)

# Convert to A2A FastAPI app (uvicorn will import this module and find `app`)
app = to_a2a(clinic_agent, port=8001)

print("DBG GOOGLE_API_KEY present?", bool(os.environ.get("GOOGLE_API_KEY")))
