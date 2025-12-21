"""
MODIFICATION NOTES:
-------------------
1. Older CLI-based constants and helper functions
   have been COMMENTED OUT (not deleted).
2. Emergency severity (HIGH / MODERATE / LOW) logic remains unchanged.
3. Specialty inference is keyword-based (NOT severity-based).
4. ✅ IMPORTANT FIX:
   Chest-related symptoms are HARD-MAPPED to CARDIOLOGY
   to ensure medical correctness.
"""

# =================================================
# 🔴 EMERGENCY KEYWORD CLASSIFICATION (UNCHANGED)
# =================================================
HIGH_RISK_KEYWORDS = [
     "heart pain", "difficulty breathing",
    "shortness of breath", "unconscious",
    "bleeding", "severe", "stroke", "seizure", "blood-vommit"
]

MODERATE_RISK_KEYWORDS = [
    "fever", "vomiting", "headache",
    "stomach pain", "dizziness", "weakness","chest pain"
]

# =================================================
# 🧠 NEW: SYMPTOM → SPECIALTY KEYWORD MAP (ADDED)
# =================================================
SPECIALTY_KEYWORDS = {
    "cardiology": [
        "chest pain",
        "heart pain",
        "shortness of breath",
        "difficulty breathing",
        "chest discomfort",
        "tightness in chest"
    ],
    "gastroenterology": [
        "stomach pain",
        "abdominal pain",
        "vomiting",
        "blood-vommit",
        "bleeding"
    ],
    "neurology": [
        "stroke",
        "seizure",
        "unconscious"
    ],
    "general_physician": [
        "fever",
        "headache",
        "dizziness",
        "weakness"
    ]
}

# =================================================
# 🧠 EMERGENCY LEVEL DETECTION (UNCHANGED)
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
# ✅ NEW: SPECIALTY INFERENCE FROM SYMPTOMS (MODIFIED)
# =================================================
def infer_specialty_from_symptoms(text: str) -> str:
    """
    Infers medical specialty based on symptom keywords.

    IMPORTANT MEDICAL RULE:
    -----------------------
    Chest-related symptoms MUST ALWAYS map to CARDIOLOGY.
    No fallback to General Physician is allowed here.
    """
    text = text.lower()

    # =================================================
    # ✅ HARD OVERRIDE: CHEST → CARDIOLOGY (ADDED)
    # =================================================
    CHEST_CRITICAL_KEYWORDS = [
        "chest pain",
        "chest discomfort",
        "tightness in chest",
        "heart pain"
    ]

    if any(k in text for k in CHEST_CRITICAL_KEYWORDS):
        return "cardiology"

    # =================================================
    # ✅ NORMAL KEYWORD-BASED MAPPING
    # =================================================
    for specialty, keywords in SPECIALTY_KEYWORDS.items():
        if any(k in text for k in keywords):
            return specialty

    # =================================================
    # ✅ SAFE FALLBACK
    # =================================================
    return "general_physician"

# =================================================
# ❌ OLD (INCORRECT): SPECIALTY FROM EMERGENCY LEVEL
# ❌ COMMENTED — DO NOT DELETE
# =================================================
# def infer_specialty_from_emergency_level(level: str) -> str:
#     if level == "HIGH":
#         return "cardiology"
#     if level == "MODERATE":
#         return "general_physician"
#     return "general_physician"

# =================================================
# 🚨 SOS MESSAGE FORMATTER (UNCHANGED)
# =================================================
def format_sos_message() -> str:
    msg = "🚨 **HIGH EMERGENCY DETECTED** 🚨\n\n"
    msg += "🚑 **Emergency Numbers:**\n- Ambulance: 108\n- Emergency: 112\n"
    msg += "\n⚠️ **Immediate Actions:**\n"
    msg += "- Sit or lie down comfortably.\n"
    msg += "- Avoid physical activity.\n"
    msg += "- Stay calm and breathe slowly.\n"
    return msg

# =================================================
# 🩺 HOME CARE FORMATTER (UNCHANGED)
# =================================================
def format_home_care() -> str:
    msg = "🩺 **Home Care Advice:**\n"
    msg += "- Take proper rest.\n"
    msg += "- Drink enough fluids.\n"
    msg += "- Monitor symptoms for 24 hours.\n"
    return msg