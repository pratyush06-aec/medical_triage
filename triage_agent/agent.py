# """
# Triage Orchestrator Agent (local)

# - Tools:
#     * classify_symptoms(symptom_text) -> {"probable_specialty", "urgency_level"}
#     * book_appointment(doctor_id, date, slot) -> booking confirmation (local in-memory)
# - Sub-agent:
#     * remote_clinic_agent: points to clinic_server's A2A agent card
#       (exposes tools: get_clinic_info(area), get_doctors(specialty, area, day),
#        get_doctor_availability(doctor_id, date_or_day))
# """

# from typing import Optional, Dict
# from google.adk.agents import LlmAgent
# from google.adk.agents.remote_a2a_agent import RemoteA2aAgent, AGENT_CARD_WELL_KNOWN_PATH
# from google.adk.models.google_llm import Gemini
# from google.genai import types


# try:
#     from dotenv import load_dotenv
#     load_dotenv()
# except Exception:
#     pass

# # Model + retry config (same pattern as clinic_server.py)
# MODEL_NAME = "gemini-2.5-flash-lite"
# retry_config = types.HttpRetryOptions(
#     attempts=2, exp_base=2, initial_delay=0.5, http_status_codes=[429, 500, 503, 504]
# )

# # --- Tool: classify symptoms (simple rule-based)
# def classify_symptoms(symptom_text: str) -> dict:
#     """
#     Very small heuristic classifier to infer a probable specialty and urgency level.
#     Returns:
#         {"probable_specialty": "<specialty>", "urgency_level": "<low|moderate|high>"}
#     """
#     text = (symptom_text or "").lower()
#     if any(w in text for w in ["chest", "heart", "palpitation", "shortness of breath", "severe"]):
#         specialty = "cardiology"
#         urgency = "high"
#     elif any(w in text for w in ["fever", "cough", "sore throat", "cold", "flu"]):
#         specialty = "general_physician"
#         urgency = "moderate"
#     elif any(w in text for w in ["ear", "nose", "throat", "hearing", "loss of smell", "hoarse"]):
#         specialty = "ent"
#         urgency = "low"
#     else:
#         specialty = "general_physician"
#         urgency = "low"
#     return {"probable_specialty": specialty, "urgency_level": urgency}

# # --- Tool: booking (simple in-memory calendar)
# # Key format: doctor_id:date -> list of slots (strings)
# BOOKINGS: Dict[str, list] = {}

# def book_appointment(doctor_id: str, date: str, slot: str) -> dict:
#     """
#     Book a slot locally (in-memory).
#     NOTE: This function does not call remote A2A; orchestration logic (LLM) should call remote sub-agent
#     get_doctor_availability first to confirm availability if desired.
#     """
#     key = f"{doctor_id}:{date}"
#     booking_slot = f"{date} {slot}"
#     booked = BOOKINGS.setdefault(key, [])
#     if booking_slot in booked:
#         return {"success": False, "message": "Slot already booked."}
#     booked.append(booking_slot)
#     confirmation_id = f"BK-{doctor_id}-{len(booked)}"
#     return {
#         "success": True,
#         "doctor_id": doctor_id,
#         "date": date,
#         "slot": slot,
#         "confirmation_id": confirmation_id,
#     }

# # --- Remote A2A sub-agent (points to local clinic server)
# # Make sure clinic_server is running (uvicorn clinic_agent.clinic_server:app --port 8001)
# remote_clinic_agent = RemoteA2aAgent(
#     name="clinic_directory_agent",
#     description="Remote clinic directory agent (provides clinic, doctor, availability info).",
#     agent_card=f"http://localhost:8001{AGENT_CARD_WELL_KNOWN_PATH}",
# )

# def _call_remote_clinic(func_name: str, args: dict) -> dict:
#     """
#     Synchronous wrapper that posts to the remote A2A agent using the ADK's helper.
#     The exact call may vary by ADK version; consult RemoteA2aAgent methods.
#     """
#     # remote_clinic_agent is the RemoteA2aAgent instance
#     # Many ADK versions allow remote_clinic_agent.call(...) or remote_clinic_agent.run(...)
#     # here's an example using a generic send call (please adapt to your ADK release)
#     resp = remote_clinic_agent.call(func_name, args)  # pseudo-code
#     return resp

# def get_doctors_local_proxy(specialty: str, area: Optional[str] = None, day: Optional[str] = None) -> dict:
#     args = {"specialty": specialty}
#     if area:
#         args["area"] = area
#     if day:
#         args["day"] = day
#     return _call_remote_clinic("get_doctors", args)


# # --- Root agent: orchestrator that can use tools & remote sub-agent
# orchestrator_agent = LlmAgent(
#     model=Gemini(model=MODEL_NAME, retry_options=retry_config),
#     name="triage_orchestrator",
#     description="Triage & appointment orchestrator agent.",
#         instruction=(
#     "You are a triage assistant. Follow this procedure when a user asks about symptoms or booking:\n"
#     "1) If the user describes symptoms, call classify_symptoms(symptom_text) to infer a probable specialty and urgency.\n"
#     "2) If the user needs clinic/doctor/availability info, DO NOT call non-local functions directly.\n"
#     "   Instead call the provided tool 'transfer_to_agent' to transfer the request to the remote clinic_directory_agent.\n"
#     "   Use this exact transfer_to_agent pattern (JSON-like) when asking the remote agent for clinic data:\n"
#     "     transfer_to_agent(agent_name='clinic_directory_agent', function='get_clinic_info', args={'area': '<area>'})\n"
#     "     transfer_to_agent(agent_name='clinic_directory_agent', function='get_doctors', args={'specialty': '<specialty>', 'area': '<area>', 'day': '<day_or_date>'})\n"
#     "     transfer_to_agent(agent_name='clinic_directory_agent', function='get_doctor_availability', args={'doctor_id': '<doctor_id>', 'date_or_day': '<date_or_weekday>'})\n"
#     "   The remote agent will run and return structured JSON. Wait for that result, then incorporate it into a friendly text reply.\n"
#     "3) If user wants to book, confirm availability (transfer to clinic_directory_agent to check) and then call book_appointment(doctor_id, date, slot) locally.\n"
#     "IMPORTANT OPTIMIZATION:\n"
# "- If urgency level is HIGH:\n"
# "  • Immediately respond with emergency advice\n"
# "  • DO NOT call the LLM again\n"
# "  • DO NOT attempt booking unless user explicitly insists\n\n"
# ),


#     tools=[classify_symptoms, book_appointment],
#     sub_agents=[remote_clinic_agent],
# )















"""
Triage Orchestrator Agent (local)

- Tools:
    * classify_symptoms(symptom_text)
    * book_appointment(doctor_id, date, slot)
- Sub-agent:
    * remote_clinic_agent (A2A)
"""

from typing import Optional, Dict
from google.adk.agents import LlmAgent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent, AGENT_CARD_WELL_KNOWN_PATH
from google.adk.models.google_llm import Gemini
from google.genai import types

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# ============================================================
# MODEL CONFIG
# ============================================================

MODEL_NAME = "gemini-2.5-flash-lite"
retry_config = types.HttpRetryOptions(
    attempts=2,
    exp_base=2,
    initial_delay=0.5,
    http_status_codes=[429, 500, 503, 504],
)

# ============================================================
# TOOLS
# ============================================================

def classify_symptoms(symptom_text: str) -> dict:
    text = (symptom_text or "").lower()
    if any(w in text for w in ["chest", "heart", "palpitation", "shortness", "severe"]):
        return {"probable_specialty": "cardiology", "urgency_level": "high"}
    elif any(w in text for w in ["fever", "cough", "cold", "flu"]):
        return {"probable_specialty": "general_physician", "urgency_level": "moderate"}
    return {"probable_specialty": "general_physician", "urgency_level": "low"}


BOOKINGS: Dict[str, list] = {}

def book_appointment(doctor_id: str, date: str, slot: str) -> dict:
    key = f"{doctor_id}:{date}"
    booked = BOOKINGS.setdefault(key, [])
    if slot in booked:
        return {"success": False, "message": "Slot already booked"}
    booked.append(slot)
    return {
        "success": True,
        "confirmation_id": f"BK-{doctor_id}-{len(booked)}"
    }

# ============================================================
# REMOTE A2A AGENT
# ============================================================

remote_clinic_agent = RemoteA2aAgent(
    name="clinic_directory_agent",
    description="Remote clinic directory agent",
    agent_card=f"http://localhost:8001{AGENT_CARD_WELL_KNOWN_PATH}",
)

# ============================================================
# ❌ OLD IMPLEMENTATION (COMMENTED – DO NOT DELETE)
# ❌ PROBLEM: Instantiates LlmAgent at import time
# ============================================================

# orchestrator_agent = LlmAgent(
#     model=Gemini(model=MODEL_NAME, retry_options=retry_config),
#     name="triage_orchestrator",
#     description="Triage & appointment orchestrator agent.",
#     instruction=INSTRUCTION_TEXT,
#     tools=[classify_symptoms, book_appointment],
#     sub_agents=[remote_clinic_agent],
# )

# ============================================================
# ✅ NEW IMPLEMENTATION (FIX)
# Lazy singleton for FastAPI + uvicorn reload safety
# ============================================================

_orchestrator_agent = None

instruction=(
    """You are a triage assistant. Follow this procedure when a user asks about symptoms or booking:

1) If the user describes symptoms, call classify_symptoms(symptom_text) to infer a probable specialty and urgency.

2) If the user needs clinic/doctor/availability info, DO NOT call non-local functions directly.
   Instead call the provided tool 'transfer_to_agent' to transfer the request to the remote clinic_directory_agent.

   Use this exact transfer_to_agent pattern:
     transfer_to_agent(agent_name='clinic_directory_agent', function='get_clinic_info', args={'area': '<area>'})
     transfer_to_agent(agent_name='clinic_directory_agent', function='get_doctors', args={'specialty': '<specialty>', 'area': '<area>', 'day': '<day_or_date>'})
     transfer_to_agent(agent_name='clinic_directory_agent', function='get_doctor_availability', args={'doctor_id': '<doctor_id>', 'date_or_day': '<date_or_weekday>'})

   Wait for the remote agent result and incorporate it into a friendly reply.

3) If the user wants to book:
   - Confirm availability via clinic_directory_agent
   - Then call book_appointment locally

IMPORTANT OPTIMIZATION:
- If urgency level is HIGH:
  • Immediately respond with emergency advice
  • DO NOT call the LLM again
  • DO NOT attempt booking unless the user explicitly insists"""
)

def get_orchestrator_agent() -> LlmAgent:
    """
    Lazily creates the orchestrator agent.
    This FIXES:
    - uvicorn reload crashes
    - UI hanging
    - ADK reinitialization bugs
    """
    global _orchestrator_agent

    if _orchestrator_agent is None:
        _orchestrator_agent = LlmAgent(
            model=Gemini(model=MODEL_NAME, retry_options=retry_config),
            name="triage_orchestrator",
            description="Triage & appointment orchestrator agent.",
            instruction=instruction,
            tools=[classify_symptoms, book_appointment],
            sub_agents=[remote_clinic_agent],
        )

    return _orchestrator_agent

