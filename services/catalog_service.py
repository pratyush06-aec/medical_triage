# from collections import defaultdict
# from database.db import get_doctors_by_area_and_specialty
# from database.db import specialty_exists_in_area
# # ✅ MODIFICATION: Import specialty inference function
# from utils.emergency_support import infer_specialty_from_symptoms


# # =================================================
# # ❌ OLD DATE-BASED LOGIC (COMMENTED — DO NOT DELETE)
# # =================================================
# # STATIC_DATE = "2025-01-15"

# # =================================================
# # ❌ OLD LOGIC (COMMENTED — DO NOT DELETE)
# # doctors[doctor_id]["schedule"][day].append(time)
# # =================================================


# # =================================================
# # ✅ GROUP DB ROWS INTO STRUCTURED DOCTOR OBJECTS
# # (UNCHANGED – DATE AGNOSTIC)
# # =================================================
# def group_doctors_with_schedule(rows):
#     doctors = {}
#     for doctor_id, name, specialty, day, time in rows:
#         if doctor_id not in doctors:
#             doctors[doctor_id] = {
#                 "doctor_id": doctor_id,
#                 "name": name,
#                 "specialty": specialty,
#                 "schedule": defaultdict(list)
#             }

#         # =================================================
#         # ❌ OLD SLOT CHECK (COMMENTED — DO NOT DELETE)
#         # =================================================
#         # if not is_slot_booked(doctor=name, date=STATIC_DATE, time=time):
#         #     doctors[doctor_id]["schedule"][day].append(time)

#         # =================================================
#         # ✅ MODIFICATION: ALWAYS SHOW SLOTS
#         # =================================================
#         doctors[doctor_id]["schedule"][day].append(time)

#     for doctor in doctors.values():
#         doctor["schedule"] = dict(doctor["schedule"])

#     return [d for d in doctors.values() if d["schedule"]]


# # =================================================
# # ✅ FORMAT DOCTOR CATALOG (UNCHANGED)
# # =================================================
# def format_doctor_catalog(doctors):
#     lines = []
#     for idx, doctor in enumerate(doctors, start=1):
#         schedule_lines = []
#         for day, slots in doctor["schedule"].items():
#             schedule_lines.append(f"     - {day}: {', '.join(slots)}")
#         lines.append(
#             f"{idx}. {doctor['name']} "
#             f"({doctor['specialty'].replace('_', ' ').title()})\n"
#             f"   Availability:\n" +
#             "\n".join(schedule_lines)
#         )
#     return "\n\n".join(lines)


# # =================================================
# # ✅ MODIFICATION: USER INTERACTION ENTRY POINT
# # THIS IS WHERE inferred_specialty MUST BE PRINTED
# # =================================================
# def handle_user_input(user_input: str, area: str) -> str:
#     """
#     Entry point for user interaction.
#     MODIFICATION:
#     - Added debug print for inferred_specialty
#     """

#     # =================================================
#     # MODIFICATION: SPECIALTY INFERENCE
#     # =================================================
#     inferred_specialty = infer_specialty_from_symptoms(user_input)

#     # 🔴 DEBUG LINE (AS REQUESTED)
#     print("DEBUG → inferred_specialty:", inferred_specialty)

#     # Safety normalization
#     inferred_specialty = inferred_specialty.strip().lower()
#     area = area.strip().lower()

#     return get_doctor_catalog(area, inferred_specialty)


# # =================================================
# # ✅ PUBLIC SERVICE FUNCTION (UNCHANGED LOGIC)
# # =================================================
# def get_doctor_catalog(area: str, specialty: str) -> str:
#     area = area.strip().lower()
#     specialty = specialty.strip().lower()

#     # =================================================
#     # STEP 1: SPECIALIST EXISTENCE CHECK
#     # =================================================
#     if not specialty_exists_in_area(area, specialty):
#         return (
#             f"❌ No {specialty.replace('_', ' ').title()} "
#             f"found in {area.title()}.\n\n"
#             "You may consult a General Physician for initial evaluation."
#         )

#     # =================================================
#     # STEP 2: SHOW SPECIALIST (ALWAYS)
#     # =================================================
#     rows = get_doctors_by_area_and_specialty(area, specialty)
#     doctors = group_doctors_with_schedule(rows)

#     if doctors:
#         return (
#             "🩺 **Available Doctors:**\n\n"
#             f"{format_doctor_catalog(doctors)}\n\n"
#             "Please choose a doctor by number."
#         )

#     return (
#         f"⚠️ A {specialty.replace('_', ' ').title()} "
#         f"is present in your area, but no schedule is currently available."
#     )


# # =================================================
# # ❌ OLD FALLBACK MAP (COMMENTED — DO NOT DELETE)
# # =================================================
# # fallback_map = {
# #     "cardiology": "general_physician",
# #     "neurology": "general_physician",
# #     "gastroenterology": "general_physician"
# # }














from collections import defaultdict
from database.db import get_doctors_by_area_and_specialty
from database.db import specialty_exists_in_area

# ✅ MODIFICATION: Import specialty inference function (USED BY handle_user_input)
from utils.emergency_support import infer_specialty_from_symptoms

# =================================================
# ❌ OLD DATE-BASED LOGIC (COMMENTED — DO NOT DELETE)
# =================================================
# STATIC_DATE = "2025-01-15"

# =================================================
# ❌ OLD LOGIC (COMMENTED — DO NOT DELETE)
# doctors[doctor_id]["schedule"][day].append(time)
# =================================================


# =================================================
# ✅ GROUP DB ROWS INTO STRUCTURED DOCTOR OBJECTS
# (UNCHANGED – DATE AGNOSTIC)
# =================================================
def group_doctors_with_schedule(rows):
    doctors = {}

    for doctor_id, name, specialty, day, time in rows:
        if doctor_id not in doctors:
            doctors[doctor_id] = {
                "doctor_id": doctor_id,
                "name": name,
                "specialty": specialty,
                "schedule": defaultdict(list)
            }

        # =================================================
        # ❌ OLD SLOT CHECK (COMMENTED — DO NOT DELETE)
        # =================================================
        # if not is_slot_booked(doctor=name, date=STATIC_DATE, time=time):
        #     doctors[doctor_id]["schedule"][day].append(time)

        # =================================================
        # ✅ MODIFICATION: ALWAYS SHOW SLOTS
        # (Booking conflicts handled at booking time)
        # =================================================
        doctors[doctor_id]["schedule"][day].append(time)

    # Convert defaultdict → dict
    for doctor in doctors.values():
        doctor["schedule"] = dict(doctor["schedule"])

    return [d for d in doctors.values() if d["schedule"]]


# =================================================
# ✅ FORMAT DOCTOR CATALOG (UNCHANGED)
# =================================================
def format_doctor_catalog(doctors):
    lines = []

    for idx, doctor in enumerate(doctors, start=1):
        schedule_lines = []
        for day, slots in doctor["schedule"].items():
            schedule_lines.append(
                f"     - {day}: {', '.join(slots)}"
            )

        lines.append(
            f"{idx}. {doctor['name']} "
            f"({doctor['specialty'].replace('_', ' ').title()})\n"
            f"   Availability:\n" +
            "\n".join(schedule_lines)
        )

    return "\n\n".join(lines)


# =================================================
# ✅ MODIFICATION: USER INTERACTION ENTRY POINT
# THIS IS WHERE inferred_specialty IS DEBUGGED
# =================================================
def handle_user_input(user_input: str, area: str):
    """
    Entry point for user interaction.
    MODIFICATION:
    - Added debug print for inferred_specialty
    """

    # =================================================
    # ✅ MODIFICATION: SPECIALTY INFERENCE
    # =================================================
    inferred_specialty = infer_specialty_from_symptoms(user_input)

    # 🔴 DEBUG LINE (AS REQUESTED)
    print("DEBUG → inferred_specialty:", inferred_specialty)

    # Safety normalization
    inferred_specialty = inferred_specialty.strip().lower()
    area = area.strip().lower()

    return get_doctor_catalog(area, inferred_specialty)


# =================================================
# ✅ PUBLIC SERVICE FUNCTION
# MODIFICATION: RETURNS STRUCTURED fallback_offer
# =================================================
def get_doctor_catalog(area: str, specialty: str):
    area = area.strip().lower()
    specialty = specialty.strip().lower()

    # =================================================
    # STEP 1: SPECIALIST EXISTENCE CHECK
    # =================================================
    if not specialty_exists_in_area(area, specialty):

        # =================================================
        # ❌ OLD STRING-ONLY FALLBACK (COMMENTED — DO NOT DELETE)
        # =================================================
        # return (
        #     f"❌ No {specialty.replace('_', ' ').title()} "
        #     f"found in {area.title()}.\n\n"
        #     "You may consult a General Physician for initial evaluation."
        # )

        # =================================================
        # ✅ MODIFICATION: STRUCTURED FALLBACK OFFER
        # (Consumed by interact.py → awaiting = fallback_consent)
        # =================================================
        return {
            "type": "fallback_offer",
            "missing_specialty": specialty,
            "fallback_specialty": "general_physician",
            "area": area
        }

    # =================================================
    # STEP 2: SHOW SPECIALIST (ALWAYS IF EXISTS)
    # =================================================
    rows = get_doctors_by_area_and_specialty(area, specialty)
    doctors = group_doctors_with_schedule(rows)

    if doctors:
        return {
            "type": "catalog",
            "specialty": specialty,
            "area": area,
            "doctors": doctors
        }

    # =================================================
    # STEP 3: SPECIALIST EXISTS BUT NO SCHEDULE
    # =================================================
    return {
        "type": "no_schedule",
        "specialty": specialty,
        "area": area
    }


# =================================================
# ❌ OLD FALLBACK MAP (COMMENTED — DO NOT DELETE)
# =================================================
# fallback_map = {
#     "cardiology": "general_physician",
#     "neurology": "general_physician",
#     "gastroenterology": "general_physician"
# }
