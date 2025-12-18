# -------------------------------------------------
# Service layer for UI / FastAPI
# Exposes SAFE async triage entrypoints
# -------------------------------------------------

# ✅ NEW IMPORT (RULE-BASED, NO LLM)
from triage_agent.agent import classify_symptoms


# -------------------------------------------------
# ✅ NEW: RULE-BASED ASYNC TRIAGE (ACTIVE)
# -------------------------------------------------
async def run_triage_async(user_input: str) -> dict:
    """
    Async entry point for UI / FastAPI layer.
    Performs rule-based triage without calling LLM.
    """
    triage = classify_symptoms(user_input)

    return {
        "urgency": triage.get("urgency_level"),
        "specialty": triage.get("probable_specialty"),
    }


# -------------------------------------------------
# ❌ OLD LOGIC (COMMENTED OUT — KEPT FOR REFERENCE)
# -------------------------------------------------

# from triage_agent.agent import get_orchestrator_agent
# import asyncio

# def run_triage(user_input: str) -> str:
#     """
#     OLD: UI + API wrapper around ADK orchestrator (LLM-based)
#     COMMENTED to avoid:
#     - Circular imports
#     - Async loop conflicts
#     - Gemini quota exhaustion
#     """
#     agent = get_orchestrator_agent()
#
#     try:
#         loop = asyncio.get_running_loop()
#     except RuntimeError:
#         loop = None
#
#     # If FastAPI event loop is running → offload
#     if loop and loop.is_running():
#         return asyncio.run(_run_agent_async(agent, user_input))
#     else:
#         return agent.run(user_input)
#
#
# async def _run_agent_async(agent, user_input: str) -> str:
#     return await asyncio.to_thread(agent.run, user_input)
#
#
# # ❌ OLD ALIAS (DISABLED)
# # run_triage_async = run_triage


# -------------------------------------------------
# ✅ PUBLIC EXPORTS (VERY IMPORTANT)
# -------------------------------------------------
__all__ = ["run_triage_async"]
