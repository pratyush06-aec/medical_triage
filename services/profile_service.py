from database.db import get_user_appointments

def get_profile(user_id: int):
    appointments = get_user_appointments(user_id)

    upcoming = [a for a in appointments if a[4] == "booked"]
    past = [a for a in appointments if a[4] != "booked"]

    return {
        "upcoming": upcoming,
        "past": past
    }
