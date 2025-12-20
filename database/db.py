import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "clinic.db"

# =================================================
# DB CONNECTION
# =================================================
def get_connection():
    return sqlite3.connect(DB_PATH)


# =================================================
# DB INITIALIZATION
# =================================================
def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # =================================================
    # ✅ EXISTING: APPOINTMENTS TABLE (UNCHANGED)
    # =================================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT NOT NULL,
            doctor TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    # =================================================
    # ✅ NEW: DOCTORS CATALOG TABLE (ADDED)
    # =================================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS doctors (
            doctor_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            specialty TEXT NOT NULL,
            area TEXT NOT NULL
        )
    """)

    # =================================================
    # ✅ NEW: DOCTOR SCHEDULE TABLE (ADDED)
    # =================================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS doctor_schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doctor_id TEXT NOT NULL,
            day TEXT NOT NULL,
            time TEXT NOT NULL,
            FOREIGN KEY (doctor_id) REFERENCES doctors (doctor_id)
        )
    """)

    conn.commit()
    conn.close()


# =================================================
# ❌ OLD: STATIC DOCTOR CATALOG (COMMENTED — DO NOT DELETE)
# =================================================
# DOCTORS = [
#     {
#         "doctor_id": "D1",
#         "name": "Dr Sharma",
#         "specialty": "cardiology",
#         "area": "salt lake",
#         "schedule": {
#             "monday": ["10:00", "11:00"],
#             "thursday": ["14:00", "15:00"]
#         }
#     }
# ]

# =================================================
# ✅ NEW: DOCTOR CATALOG INSERT HELPERS (ADDED)
# =================================================
def add_doctor(doctor_id, name, specialty, area):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO doctors (doctor_id, name, specialty, area)
        VALUES (?, ?, ?, ?)
    """, (doctor_id, name, specialty, area))

    conn.commit()
    conn.close()


def add_doctor_schedule(doctor_id, day, time):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO doctor_schedule (doctor_id, day, time)
        VALUES (?, ?, ?)
    """, (doctor_id, day, time))

    conn.commit()
    conn.close()


# =================================================
# ✅ NEW: CATALOG QUERY HELPERS (DB‑BASED)
# =================================================
def get_doctors_by_area_and_specialty(area: str, specialty: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT d.doctor_id, d.name, d.specialty, s.day, s.time
        FROM doctors d
        JOIN doctor_schedule s ON d.doctor_id = s.doctor_id
        WHERE d.area = ? AND d.specialty = ?
        ORDER BY d.name, s.day
    """, (area.lower(), specialty.lower()))

    rows = cursor.fetchall()
    conn.close()

    return rows


# =================================================
# EXISTING: APPOINTMENT LOGIC (UNCHANGED)
# =================================================
def create_appointment(patient_name, doctor, date, time):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO appointments (patient_name, doctor, date, time, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (
        patient_name,
        doctor,
        date,
        time,
        datetime.utcnow().isoformat()
    ))

    conn.commit()
    conn.close()


def get_appointments():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM appointments")
    rows = cursor.fetchall()

    conn.close()
    return rows


def is_slot_booked(doctor, date, time):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 1 FROM appointments
        WHERE doctor = ? AND date = ? AND time = ?
        LIMIT 1
    """, (doctor, date, time))

    exists = cursor.fetchone() is not None
    conn.close()
    return exists
