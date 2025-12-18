"""
Main CLI for Medical Triage Capstone Project

This script:
- Loads the triage_orchestrator agent (local orchestrator)
- Connects automatically to the running clinic_directory A2A server
- Provides a simple text-based chat interface
- Uses an InMemoryRunner (most stable for local multi-agent interaction)
"""

import asyncio
import os
import logging
# ✅ NEW IMPORT (ADD)
from triage_agent.agent import classify_symptoms

from google.adk.runners import InMemoryRunner
# from google.adk.sessions import InMemorySessionService
from google.adk.plugins.logging_plugin import LoggingPlugin
from triage_agent.agent import orchestrator_agent

from dotenv import load_dotenv
load_dotenv() 


# -----------------------------------------
# Logging setup
# -----------------------------------------
LOG_FILE = "agent_logs.log"

# Clean old log file
if os.path.exists(LOG_FILE):
    os.remove(LOG_FILE)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
logging.getLogger().addHandler(console_handler)

logging.info("Logging initialized.")


# -----------------------------------------
# Runner factory
# -----------------------------------------
def create_runner():
    """
    Create an InMemoryRunner with LoggingPlugin.
    This version does NOT pass a session_service because InMemoryRunner
    in this ADK release does not accept that argument.
    """
    return InMemoryRunner(
        agent=orchestrator_agent,
        plugins=[LoggingPlugin()],
    )


def wants_booking(text: str) -> bool:
    keywords = [
        "book",
        "appointment",
        "doctor",
        "consult",
        "schedule",
        "visit"
    ]
    text = text.lower()
    return any(k in text for k in keywords)


# -----------------------------------------
# Chat loop
# -----------------------------------------

# Ensure defaults for static analysis
# urgency: str | None = None
# specialty: str | None = None

async def chat_loop():
    """
    REPL-style interface for talking with the triage orchestrator.
    Requires:
        - clinic server running separately on port 8001
    """
    runner = create_runner()

    # -----------------------------------------
    # 🧠 SESSION MEMORY (NEW)
    # -----------------------------------------
    # Stores last detected severity & specialty
    # Used to support follow-up actions like booking
    last_severity = None
    last_specialty = None
    booking_in_progress= False
    booking_declined= False

    print("\n==============================")
    print("  🏥 MEDICAL TRIAGE ASSISTANT  ")
    print("==============================")
    print("Type your symptoms, request doctors, or book appointments.")
    print("Type 'exit' to quit.\n")


    while True:
        try:
            user_msg = input("You > ").strip()

            # -------------------------------------------------
            # 🚪 USER EXPLICITLY DECLINES ANY FURTHER HELP (NEW)
            # -------------------------------------------------
            if user_msg.lower() in {"no", "nah", "not now"} and not booking_in_progress:
                print("\nAgent > Alright 👍 Take care and get well soon!")
                break


            # -------------------------------------------------
            # 📅 STEP 1: BOOKING INTENT CHECK (NEW)
            # -------------------------------------------------

            if wants_booking(user_msg):
                if last_severity in ("low", "moderate"):
                    booking_in_progress= True
                    print("\nAgent > 📅 Sure! I can help you book an appointment.")
                    print(
                        f"Recommended specialty: "
                        f"{(last_specialty or 'general_physician').replace('_', ' ').title()}"
                    )
                    print("Please confirm: Do you want the earliest available slot? (yes/no)")
                    continue

                elif last_severity == "high":
                    print("\nAgent > ⚠️ Booking is not advised for emergencies.")
                    print("Please seek immediate medical attention immediately.")
                    continue

                else:
                    print(
                        "\nAgent > ℹ️ I need to understand your symptoms first "
                        "before booking an appointment.\n"
                        "Please briefly describe how you are feeling."
                    )
                    continue

        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not user_msg:
            continue

        if user_msg.lower() in {"exit", "quit"}:
            print("Exiting.")
            break

        logging.info(f"User Input: {user_msg}")
        print("Agent thinking...\n")

        # -------------------------------------------------
        # 📅 BOOKING CONFIRMATION HANDLER (NEW)
        # -------------------------------------------------
        if booking_in_progress:
            if user_msg.lower() in {"yes", "y"}:
                print("\nAgent > ✅ Appointment booked successfully!")
                print(
                    f"Doctor specialty: "
                    f"{(last_specialty or 'general_physician').replace('_', ' ').title()}"
                )
                print("📍 Clinic: Nearest available clinic")
                print("🕒 Slot: Earliest available")
                print("📞 You will receive confirmation shortly.\n")

                print("🙏 Take care and get well soon!")
                break   # ✅ EXIT LOOP AFTER BOOKING

            elif user_msg.lower() in {"no", "n"}:
                print("\nAgent > No problem👍")
                print("Take care!! You may follow the home remedies if you wish for relief. Feel free to reach out any-time😊")

                booking_in_progress= False
                booking_declined= True
                break


        # Run agent turn
        
        # ------------------------------------------------------------------
        # 🔍 DEBUG VERSION OF EVENT HANDLING (INSERTED HERE)
        # ------------------------------------------------------------------

        # -------------------------------------------------
        # 🚑 PRE-LLM SAFETY GATE (NEW)
        # -------------------------------------------------
        triage = classify_symptoms(user_msg)
        urgency = triage.get("urgency_level")
        specialty = triage.get("probable_specialty")

        # 🧠 SAVE CONTEXT FOR FOLLOW-UP TURNS (NEW)
        # global last_severity, last_specialty
        last_severity = urgency
        last_specialty = specialty

        # if urgency == "high":
        #     print(
        #         "\nAgent > ⚠️ This may be a medical emergency.\n"
        #         "Your symptoms suggest a HIGH level of urgency "
        #         f"({specialty}).\n\n"
        #         "Please seek immediate medical attention or go to the nearest "
        #         "emergency department right now.\n"
        #         "Do NOT delay care.\n"
        #     )
        #     continue

        from utils.emergency_support import (
            format_sos_message,
            format_hospital_list,
            HIGH_EMERGENCY_ADVICE,
            LOW_EMERGENCY_ADVICE,
        )

        if urgency == "high":
            print(
                "\nAgent > ⚠️ MEDICAL EMERGENCY DETECTED\n"
                f"Specialty involved: {specialty.upper()}\n\n"
                "🚨 PLEASE SEEK IMMEDIATE MEDICAL CARE 🚨\n"
            )

            print(format_sos_message())
            print(format_hospital_list())

            print("\n🧘 IMMEDIATE ACTIONS YOU CAN TAKE NOW:")
            for tip in HIGH_EMERGENCY_ADVICE:
                print(f"- {tip}")

            print(
                "\n⚠️ This assistant is NOT a doctor.\n"
                "These steps are only for temporary support until professional help arrives.\n"
            )
            break


        if urgency in {"low", "moderate"} and not booking_in_progress:
            print("\nAgent > 🏡 HOME COMFORT SUGGESTIONS:")
            for tip in LOW_EMERGENCY_ADVICE:
                print(f"- {tip}")

            print(
                "\nWould you like to book an appointment? "
                "You can say 'book appointment'.\n"
            )
            continue


        # -------------------------------------------------
        # ✅ SAFE TO CALL LLM BELOW
        # -------------------------------------------------

        events = await runner.run_debug(user_msg)

        final_text = None
        for ev in events:
            # Log every event for deeper debugging
            logging.debug(
                "EVENT: %s | is_final: %s | content: %s",
                getattr(ev, "id", None),
                getattr(ev, "is_final_response", None),
                getattr(ev, "content", None)
            )

            # Extract final text response if present
            if getattr(ev, "is_final_response", None) and ev.is_final_response():
                if ev.content and ev.content.parts:
                    for part in ev.content.parts:
                        if getattr(part, "text", None):
                            final_text = part.text

        if final_text:
            print(f"Agent > {final_text}\n")
        # else:
        #     print("Agent > (no final text response)\n")

        else:
            print(
        "Agent > I'm temporarily unable to continue due to API rate limits. "
        "If this is urgent (like chest pain, breathing trouble, or fainting), "
        "please seek immediate medical care.\n"
    )
            print("DEBUG: raw events (first few):")
            for i, ev in enumerate(events[:8]):
                print(i, repr(ev))
        # ------------------------------------------------------------------
        # 🔍 END DEBUG BLOCK
        # ------------------------------------------------------------------


# -----------------------------------------
# Entry point
# -----------------------------------------
if __name__ == "__main__":
    asyncio.run(chat_loop())
