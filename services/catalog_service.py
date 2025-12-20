# =================================================
# CATALOG SERVICE
# Responsible ONLY for formatting and structuring data
# =================================================

from collections import defaultdict
from database.db import get_doctors_by_area_and_specialty

# =================================================
# ❌ OLD: INLINE GROUPING + FORMATTING LOGIC
# COMMENTED — DO NOT DELETE
# (This version grouped rows and formatted output here,
# which mixed responsibilities and duplicated logic)
# =================================================
# def get_doctor_catalog(area: str, specialty: str) -> str:
#     rows = get_doctors_by_area_and_specialty(area, specialty)
#     if not rows:
#         return "No doctors found in your area."
#
#     doctors = defaultdict(lambda: defaultdict(list))
#     for doctor_id, name, specialty, day, time in rows:
#         doctors[name]["specialty"] = specialty
#         doctors[name][day].append(time)
#
#     msg = "🩺 **Available Doctors:**\n\n"
#     for name, info in doctors.items():
#         msg += f"- {name} ({info['specialty'].replace('_',' ').title()})\n"
#         for day, slots in info.items():
#             if day == "specialty":
#                 continue
#             msg += f"   {day.title()}: {', '.join(slots)}\n"
#         msg += "\n"
#
#     msg += "Please tell me the doctor name, day, and time."
#     return msg

# =================================================
# ❌ OLD: SIMPLE CATALOG FORMATTER (COMMENTED — DO NOT DELETE)
# =================================================
# def format_doctor_catalog(doctors):
#     return "\n".join([doc["name"] for doc in doctors])

# =================================================
# ✅ NEW: GROUP DB ROWS INTO STRUCTURED DOCTOR OBJECTS
# =================================================
def group_doctors_with_schedule(rows):
    """
    Converts flat DB rows into structured doctor objects.

    Input row format:
    (doctor_id, name, specialty, day, time)
    """

    doctors = {}

    for doctor_id, name, specialty, day, time in rows:
        if doctor_id not in doctors:
            doctors[doctor_id] = {
                "doctor_id": doctor_id,
                "name": name,
                "specialty": specialty,
                "schedule": defaultdict(list)
            }

        doctors[doctor_id]["schedule"][day].append(time)

    # Convert defaultdict → normal dict for clean output
    for doctor in doctors.values():
        doctor["schedule"] = dict(doctor["schedule"])

    return list(doctors.values())

# =================================================
# ✅ NEW: FORMAT STRUCTURED DOCTOR CATALOG FOR DISPLAY
# =================================================
def format_doctor_catalog(doctors):
    """
    Formats doctor catalog with availability for user display.
    """

    lines = []

    for idx, doctor in enumerate(doctors, start=1):
        schedule_lines = []

        for day, slots in doctor["schedule"].items():
            schedule_lines.append(
                f"     - {day}: {', '.join(slots)}"
            )

        schedule_text = "\n".join(schedule_lines)

        lines.append(
            f"{idx}. {doctor['name']} "
            f"({doctor['specialty'].replace('_', ' ').title()})\n"
            f"   Availability:\n{schedule_text}"
        )

    return "\n\n".join(lines)

# =================================================
# ✅ NEW: PUBLIC SERVICE FUNCTION USED BY interact.py
# =================================================
def get_doctor_catalog(area: str, specialty: str) -> str:
    """
    Fetches doctor catalog for a given area and specialty.
    Delegates:
    - DB querying → db.py
    - Grouping → group_doctors_with_schedule
    - Formatting → format_doctor_catalog
    """

    rows = get_doctors_by_area_and_specialty(area, specialty)

    if not rows:
        return "No doctors found in your area."

    # =================================================
    # ✅ MODIFICATION DONE HERE:
    # Flat DB rows → structured doctor objects
    # =================================================
    doctors = group_doctors_with_schedule(rows)

    # =================================================
    # ✅ MODIFICATION DONE HERE:
    # Structured doctors → formatted catalog text
    # =================================================
    catalog_text = format_doctor_catalog(doctors)

    return (
        "🩺 **Available Doctors:**\n\n"
        f"{catalog_text}\n\n"
        "Please choose a doctor by number."
    )