from database.db import get_doctors_by_area_and_specialty
from collections import defaultdict

def get_doctor_catalog(area: str, specialty: str) -> str:
    rows = get_doctors_by_area_and_specialty(area, specialty)

    if not rows:
        return "No doctors found in your area."

    # Group by doctor
    doctors = defaultdict(lambda: defaultdict(list))

    for doctor_id, name, specialty, day, time in rows:
        doctors[name]["specialty"] = specialty
        doctors[name][day].append(time)

    msg = "🩺 **Available Doctors:**\n\n"

    for name, info in doctors.items():
        msg += f"- {name} ({info['specialty'].replace('_',' ').title()})\n"
        for day, slots in info.items():
            if day == "specialty":
                continue
            msg += f"   {day.title()}: {', '.join(slots)}\n"
        msg += "\n"

    msg += "Please tell me the doctor name, day, and time."
    return msg
