from database.db import (
    is_slot_booked,
    create_appointment,
    get_appointments
)


def book_appointment(data: dict):
    doctor = data["doctor"]
    date = data["date"]
    time = data["time"]

    if is_slot_booked(doctor, date, time):
        return False, "Slot already booked"

    create_appointment(
        patient_name=data["patient_name"],
        doctor=doctor,
        date=date,
        time=time
    )

    return True, "Appointment booked successfully"


def list_appointments():
    return get_appointments()
