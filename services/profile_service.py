from datetime import datetime
from database.db import get_user_appointments


WEEKDAYS = {
    "Monday", "Tuesday", "Wednesday",
    "Thursday", "Friday", "Saturday", "Sunday"
}


def get_user_appointment_summary(user_id: int):
    appointments = get_user_appointments(user_id)

    upcoming = []
    past = []

    now = datetime.now()

    for appt in appointments:
        appt = list(appt)

        date = None
        time = None
        doctor = None
        weekday = None

        for item in appt:
            if not isinstance(item, str):
                continue

            # ✅ calendar date (YYYY-MM-DD)
            if "-" in item and len(item) == 10:
                date = item

            # ✅ time slot
            elif ":" in item:
                time = item

            # ✅ weekday name
            elif item in WEEKDAYS:
                weekday = item

            # ✅ doctor name (first unmatched string)
            elif doctor is None:
                doctor = item

        # =================================================
        # ❌ OLD (weekday bookings were dropped)
        # =================================================
        # if not date or not time:
        #     continue

        # =================================================
        # ✅ FIX: show weekday-based bookings
        # =================================================
        if not date:
            if weekday:
                upcoming.append({
                    "doctor": doctor or "Unknown",
                    "date": weekday,
                    "time": time or "N/A"
                })
            continue

        try:
            appt_datetime = datetime.strptime(
                f"{date} {time[:5]}",
                "%Y-%m-%d %H:%M"
            )
        except Exception:
            continue

        record = {
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
