# # -------------------------------------------------
# # 🚑 SOS CONTACT NUMBERS (India)
# # -------------------------------------------------
# SOS_CONTACTS = {
#     "ambulance": "108",
#     # "emergency_general": "112",
#     # "women_helpline": "181",
# }

# # -------------------------------------------------
# # 🏥 DEMO NEARBY HOSPITALS (STATIC, REALISTIC)
# # -------------------------------------------------
# NEARBY_HOSPITALS = [
#     {
#         "name": "District Government Hospital",
#         "address": "Main Road, City Center",
#         "contact": "033-1234-5678",
#     },
#     {
#         "name": "Apollo Clinic",
#         "address": "Park Street, Kolkata",
#         "contact": "033-2468-1357",
#     },
#     {
#         "name": "Fortis Hospital",
#         "address": "EM Bypass, Kolkata",
#         "contact": "033-4001-0000",
#     },
# ]

# # -------------------------------------------------
# # 🏠 SAFE IMMEDIATE ACTIONS (HIGH EMERGENCY)
# # -------------------------------------------------
# HIGH_EMERGENCY_ADVICE = [
#     "Sit or lie down in a comfortable position.",
#     "Avoid physical exertion or movement.",
#     "Loosen tight clothing.",
#     "Try to stay calm and take slow, deep breaths.",
#     "Do NOT eat or drink anything unless advised by a medical professional.",
# ]

# # -------------------------------------------------
# # 🏡 HOME CARE (LOW / MODERATE)
# # -------------------------------------------------
# LOW_EMERGENCY_ADVICE = [
#     "Take adequate rest.",
#     "Drink water to stay hydrated.",
#     "Avoid screens and bright lights if experiencing headache.",
#     "Use a cold or warm compress if it provides comfort.",
#     "Maintain a relaxed posture and avoid stress.",
# ]

# def format_sos_message() -> str:
#     msg = "\n🚑 EMERGENCY CONTACTS:\n"
#     for k, v in SOS_CONTACTS.items():
#         msg += f"- {k.replace('_',' ').title()}: {v}\n"
#     return msg


# def format_hospital_list() -> str:
#     msg = "\n🏥 NEARBY HOSPITALS:\n"
#     for h in NEARBY_HOSPITALS:
#         msg += (
#             f"- {h['name']}\n"
#             f"  📍 {h['address']}\n"
#             f"  ☎️ {h['contact']}\n"
#         )
#     return msg













"""
MODIFICATION NOTES:
-------------------
1. Older CLI-based constants and helper functions
   have been COMMENTED OUT (not deleted).
2. New emergency triage logic (HIGH / MODERATE / LOW)
   has been ADDED for web/UI integration.
3. New formatter functions combine SOS + hospital
   + advice in a single response.
"""

# =================================================
# 🔴 NEW: EMERGENCY KEYWORD CLASSIFICATION (WEB/UI)
# =================================================

# NEW
HIGH_RISK_KEYWORDS = [
    "chest pain", "heart pain", "difficulty breathing",
    "shortness of breath", "unconscious",
    "bleeding","severe", "stroke", "seizure", "blood-vommit"
]

# NEW
MODERATE_RISK_KEYWORDS = [
    "fever", "vomiting", "headache",
    "stomach pain", "dizziness", "weakness"
]

# =================================================
# 🚑 SOS CONTACT NUMBERS (India)
# =================================================

# MODIFIED: kept same data, standardized keys
SOS_CONTACTS = {
    "Ambulance": "108",
    "Emergency": "112",
}

# -------------------------------------------------
# ❌ OLD (CLI VERSION — COMMENTED)
# -------------------------------------------------
# SOS_CONTACTS = {
#     "ambulance": "108",
#     # "emergency_general": "112",
#     # "women_helpline": "181",
# }

# =================================================
# 🏥 DEMO NEARBY HOSPITALS (STATIC)
# =================================================

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

# =================================================
# 🏠 SAFE IMMEDIATE ACTIONS (HIGH EMERGENCY)
# =================================================

HIGH_EMERGENCY_ADVICE = [
    "Sit or lie down comfortably.",
    "Avoid any physical activity.",
    "Loosen tight clothing.",
    "Stay calm and breathe slowly.",
    "Do NOT eat or drink anything.",
]

# -------------------------------------------------
# ❌ OLD (CLI VERSION — COMMENTED)
# -------------------------------------------------
# HIGH_EMERGENCY_ADVICE = [
#     "Sit or lie down in a comfortable position.",
#     "Avoid physical exertion or movement.",
#     "Loosen tight clothing.",
#     "Try to stay calm and take slow, deep breaths.",
#     "Do NOT eat or drink anything unless advised by a medical professional.",
# ]

# =================================================
# 🏡 HOME CARE (LOW / MODERATE)
# =================================================

LOW_EMERGENCY_ADVICE = [
    "Take proper rest.",
    "Drink enough fluids.",
    "Avoid stress and exertion.",
    "Monitor symptoms for 24 hours.",
]

# -------------------------------------------------
# ❌ OLD (CLI VERSION — COMMENTED)
# -------------------------------------------------
# LOW_EMERGENCY_ADVICE = [
#     "Take adequate rest.",
#     "Drink water to stay hydrated.",
#     "Avoid screens and bright lights if experiencing headache.",
#     "Use a cold or warm compress if it provides comfort.",
#     "Maintain a relaxed posture and avoid stress.",
# ]

# =================================================
# 🧠 NEW: EMERGENCY LEVEL DETECTION
# =================================================

def detect_emergency_level(text: str) -> str:
    """
    Returns: HIGH | MODERATE | LOW
    """
    text = text.lower()

    if any(k in text for k in HIGH_RISK_KEYWORDS):
        return "HIGH"

    if any(k in text for k in MODERATE_RISK_KEYWORDS):
        return "MODERATE"

    return "LOW"


# =================================================
# 🚨 NEW: SOS MESSAGE FORMATTER (WEB/UI)
# =================================================

def format_sos_message() -> str:
    msg = "🚨 **HIGH EMERGENCY DETECTED** 🚨\n\n"

    msg += "🚑 **Emergency Numbers:**\n"
    for k, v in SOS_CONTACTS.items():
        msg += f"- {k}: {v}\n"

    msg += "\n🏥 **Nearby Hospitals:**\n"
    for h in NEARBY_HOSPITALS:
        msg += f"- {h['name']} ({h['contact']})\n"

    msg += "\n⚠️ **Immediate Actions:**\n"
    for a in HIGH_EMERGENCY_ADVICE:
        msg += f"- {a}\n"

    return msg


# -------------------------------------------------
# ❌ OLD (CLI VERSION — COMMENTED)
# -------------------------------------------------
# def format_sos_message() -> str:
#     msg = "\n🚑 EMERGENCY CONTACTS:\n"
#     for k, v in SOS_CONTACTS.items():
#         msg += f"- {k.replace('_',' ').title()}: {v}\n"
#     return msg


# =================================================
# 🩺 NEW: HOME CARE FORMATTER (LOW / MODERATE)
# =================================================

def format_home_care() -> str:
    msg = "🩺 **Home Care Advice:**\n"
    for a in LOW_EMERGENCY_ADVICE:
        msg += f"- {a}\n"
    return msg


# -------------------------------------------------
# ❌ OLD (CLI VERSION — COMMENTED)
# -------------------------------------------------
# def format_hospital_list() -> str:
#     msg = "\n🏥 NEARBY HOSPITALS:\n"
#     for h in NEARBY_HOSPITALS:
#         msg += (
#             f"- {h['name']}\n"
#             f"  📍 {h['address']}\n"
#             f"  ☎️ {h['contact']}\n"
#         )
#     return msg
