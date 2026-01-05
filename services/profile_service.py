from datetime import datetime

# =================================================
# ❌ LEGACY IMPORT (PRESERVED)
# -------------------------------------------------
# get_user_appointments is still used below
# =================================================
from database.db import get_user_appointments

# =================================================
# ✅ MODIFICATION: DB CONNECTION FOR WRITE OPERATIONS
# -------------------------------------------------
# REQUIRED for cancel_appointment_db
# =================================================
from database.db import get_connection


WEEKDAYS = {
    "Monday", "Tuesday", "Wednesday",
    "Thursday", "Friday", "Saturday", "Sunday"
}

def get_user_profile_appointments(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            doctor,
            date,
            time,
            created_at
        FROM appointments
        WHERE user_id = ?
          AND status = 'booked'
        ORDER BY created_at DESC
    """, (user_id,))

    rows = cursor.fetchall()
    conn.close()
    return rows


# =================================================
# ✅ EXISTING FUNCTION (UNCHANGED STRUCTURE)
# =================================================
def get_user_appointment_summary(user_id: int):
    appointments = get_user_profile_appointments(user_id)

    upcoming = []
    past = []

    for appt in appointments:
        appointment_id, doctor, date, time, created_at = appt

        record = {
            "id": appointment_id,
            "doctor": doctor,
            "date": date,
            "time": time
        }

        # 🔒 Until real dates are stored, treat all booked as upcoming
        upcoming.append(record)

    return {
        "upcoming": upcoming,
        "past": past
    }




# =================================================
# ✅ MODIFICATION: USER-SCOPED CANCEL FUNCTION
# -------------------------------------------------
# Called from interact.py
# MUST live in profile_service.py
# =================================================
def cancel_appointment_db(appointment_id, user_id):
    conn = get_connection()
    conn.execute(
        """
        UPDATE appointments
        SET status='cancelled'
        WHERE id=? AND user_id=? AND status='booked'
        """,
        (appointment_id, user_id)
    )
    conn.commit()


# =================================================
# ✅ MODIFICATION: ACTIVE APPOINTMENTS FOR CHAT FLOW
# -------------------------------------------------
# Used by interact.py (cancel / reschedule)
# Returns ONLY booked, upcoming appointments
# =================================================
def get_user_active_appointments(user_id: int):
    summary = get_user_appointment_summary(user_id)

    # Only upcoming appointments are cancellable
    return summary.get("upcoming", [])

