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
    # appointments = get_user_appointments(user_id)
    appointments = get_user_profile_appointments(user_id)

    upcoming = []
    past = []

    now = datetime.now()

    # =================================================
    # ❌ OLD LOOP (COMMENTED — DO NOT DELETE)
    # -------------------------------------------------
    # for appt in appointments:
    #     appt = list(appt)
    #
    #     date = None
    #     time = None
    #     doctor = None
    #     weekday = None
    # =================================================

    for appt in appointments:
        appt = list(appt)

        # =================================================
        # ✅ MODIFICATION: Extract appointment ID + status
        # -------------------------------------------------
        # ID is REQUIRED for cancel functionality
        # Status is REQUIRED to hide cancelled appointments
        # =================================================
        appointment_id = None
        status = None

        for item in appt:
            if isinstance(item, int):
                appointment_id = item
            elif isinstance(item, str) and item.lower() in ("booked", "cancelled"):
                status = item.lower()

        # =================================================
        # 🔴 CRITICAL FIX
        # -------------------------------------------------
        # Cancelled appointments MUST NOT appear in profile
        # =================================================
        if status != "booked":
            continue

        # date = None
        # time = None
        # doctor = None
        # weekday = None

        # for item in appt:
        #     if not isinstance(item, str):
        #         continue

        #     # ✅ calendar date (YYYY-MM-DD)
        #     if "-" in item and len(item) == 10:
        #         date = item

        #     # ✅ time slot
        #     elif ":" in item:
        #         time = item

        #     # ✅ weekday name
        #     elif item in WEEKDAYS:
        #         weekday = item

        #     # ✅ doctor name (first unmatched string)
        #     elif doctor is None:
        #         doctor = item

        # =================================================
        # ❌ OLD LOGIC (COMMENTED — DO NOT DELETE)
        # -------------------------------------------------
        # if not date or not time:
        #     continue
        # =================================================

        # =================================================
        # ✅ FIX: show weekday-based bookings
        # =================================================
        # if not date:
        #     if weekday:
        #         upcoming.append({
        #             # ❌ OLD (NO ID — COMMENTED)
        #             # "doctor": doctor or "Unknown",
        #             # "date": weekday,
        #             # "time": time or "N/A"

        #             # ✅ MODIFICATION: include appointment ID
        #             "id": appointment_id,
        #             "doctor": doctor or "Unknown",
        #             "date": weekday,
        #             "time": time or "N/A"
        #         })
        #     continue

        # try:
        #     appt_datetime = datetime.strptime(
        #         f"{date} {time[:5]}",
        #         "%Y-%m-%d %H:%M"
        #     )
        # except Exception:
        #     continue

        # =================================================
        # ❌ OLD RECORD (COMMENTED — DO NOT DELETE)
        # -------------------------------------------------
        # record = {
        #     "doctor": doctor or "Unknown",
        #     "date": date,
        #     "time": time
        # }
        # =================================================

        # =================================================
        # ✅ MODIFICATION: record WITH appointment ID
        # -------------------------------------------------
        # This FIXES the "Invalid appointment" issue
        # =================================================
        # record = {
        #     "id": appointment_id,        # 🔥 REQUIRED
        #     "doctor": doctor or "Unknown",
        #     "date": date,
        #     "time": time
        # }

        record = {
            "id": appointment_id,
            "doctor": doctor or "Unknown",
            "date": date,
            "time": time
        }

        if appt_datetime >= now:
            upcoming.append(record)
        else:
            past.append(record)

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

