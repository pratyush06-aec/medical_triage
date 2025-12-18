# -------------------------------------------------
# 🚑 SOS CONTACT NUMBERS (India)
# -------------------------------------------------
SOS_CONTACTS = {
    "ambulance": "108",
    # "emergency_general": "112",
    # "women_helpline": "181",
}

# -------------------------------------------------
# 🏥 DEMO NEARBY HOSPITALS (STATIC, REALISTIC)
# -------------------------------------------------
NEARBY_HOSPITALS = [
    {
        "name": "District Government Hospital",
        "address": "Main Road, City Center",
        "contact": "033-1234-5678",
    },
    {
        "name": "Apollo Clinic",
        "address": "Park Street, Kolkata",
        "contact": "033-2468-1357",
    },
    {
        "name": "Fortis Hospital",
        "address": "EM Bypass, Kolkata",
        "contact": "033-4001-0000",
    },
]

# -------------------------------------------------
# 🏠 SAFE IMMEDIATE ACTIONS (HIGH EMERGENCY)
# -------------------------------------------------
HIGH_EMERGENCY_ADVICE = [
    "Sit or lie down in a comfortable position.",
    "Avoid physical exertion or movement.",
    "Loosen tight clothing.",
    "Try to stay calm and take slow, deep breaths.",
    "Do NOT eat or drink anything unless advised by a medical professional.",
]

# -------------------------------------------------
# 🏡 HOME CARE (LOW / MODERATE)
# -------------------------------------------------
LOW_EMERGENCY_ADVICE = [
    "Take adequate rest.",
    "Drink water to stay hydrated.",
    "Avoid screens and bright lights if experiencing headache.",
    "Use a cold or warm compress if it provides comfort.",
    "Maintain a relaxed posture and avoid stress.",
]

def format_sos_message() -> str:
    msg = "\n🚑 EMERGENCY CONTACTS:\n"
    for k, v in SOS_CONTACTS.items():
        msg += f"- {k.replace('_',' ').title()}: {v}\n"
    return msg


def format_hospital_list() -> str:
    msg = "\n🏥 NEARBY HOSPITALS:\n"
    for h in NEARBY_HOSPITALS:
        msg += (
            f"- {h['name']}\n"
            f"  📍 {h['address']}\n"
            f"  ☎️ {h['contact']}\n"
        )
    return msg
