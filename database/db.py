# import sqlite3
# from datetime import datetime
# from pathlib import Path

# # =================================================
# # ✅ SYNTHETIC DOCTOR CATALOG DATA (UNCHANGED)
# # =================================================
# DOCTOR_CATALOG = [
#     {
#         "doctor_id": 1,
#         "name": "Dr. Ananya Sen",
#         "specialty": "cardiology",
#         "area": "salt lake",
#         "schedule": {
#             "Monday": ["10:00-11:00", "11:00-12:00"],
#             "Thursday": ["15:00-17:00"]
#         }
#     },
#     {
#         "doctor_id": 2,
#         "name": "Dr. Rakesh Malhotra",
#         "specialty": "gastroenterology",
#         "area": "salt lake",
#         "schedule": {
#             "Tuesday": ["09:00-10:00", "10:00-11:00"],
#             "Friday": ["14:00-16:00"]
#         }
#     },
#     {
#         "doctor_id": 3,
#         "name": "Dr. Nivedita Roy",
#         "specialty": "neurology",
#         "area": "ballygunge",
#         "schedule": {
#             "Monday": ["16:00-17:00"],
#             "Wednesday": ["10:00-12:00"]
#         }
#     },
#     {
#         "doctor_id": 4,
#         "name": "Dr. Arjun Mehta",
#         "specialty": "general_physician",
#         "area": "salt lake",
#         "schedule": {
#             "Monday": ["09:00-11:00"],
#             "Wednesday": ["09:00-11:00"],
#             "Saturday": ["10:00-12:00"]
#         }
#     },
#     {
#         "doctor_id": 5,
#         "name": "Dr. Sneha Kapoor",
#         "specialty": "dermatology",
#         "area": "new town",
#         "schedule": {
#             "Tuesday": ["11:00-13:00"],
#             "Thursday": ["10:00-12:00"]
#         }
#     },
#     {
#         "doctor_id": 6,
#         "name": "Dr. Amit Chatterjee",
#         "specialty": "orthopedics",
#         "area": "new town",
#         "schedule": {
#             "Monday": ["14:00-16:00"],
#             "Friday": ["09:00-11:00"]
#         }
#     },
#     {
#         "doctor_id": 7,
#         "name": "Dr. Priya Mukherjee",
#         "specialty": "gastroenterology",
#         "area": "ballygunge",
#         "schedule": {
#             "Wednesday": ["13:00-15:00"],
#             "Saturday": ["10:00-11:00"]
#         }
#     },
#     {
#         "doctor_id": 8,
#         "name": "Dr. Kunal Verma",
#         "specialty": "neurology",
#         "area": "salt lake",
#         "schedule": {
#             "Tuesday": ["15:00-17:00"],
#             "Friday": ["11:00-12:00"]
#         }
#     },
#     {
#         "doctor_id": 9,
#         "name": "Dr. Sharmila Das",
#         "specialty": "general_physician",
#         "area": "new town",
#         "schedule": {
#             "Monday": ["08:00-10:00"],
#             "Thursday": ["08:00-10:00"]
#         }
#     },
#     {
#         "doctor_id": 10,
#         "name": "Dr. Vikram Sood",
#         "specialty": "cardiology",
#         "area": "ballygunge",
#         "schedule": {
#             "Tuesday": ["10:00-12:00"],
#             "Saturday": ["11:00-13:00"]
#         }
#     }
# ]

# DB_PATH = Path(__file__).parent / "clinic.db"

# # =================================================
# # DB CONNECTION
# # =================================================
# def get_connection():
#     return sqlite3.connect(DB_PATH)

# # =================================================
# # DB INITIALIZATION
# # =================================================
# def init_db():
#     conn = get_connection()
#     cursor = conn.cursor()

#     # =================================================
#     # ❌ OLD APPOINTMENTS TABLE (COMMENTED — DO NOT DELETE)
#     # =================================================
#     # cursor.execute("""
#     #     CREATE TABLE IF NOT EXISTS appointments (
#     #         id INTEGER PRIMARY KEY AUTOINCREMENT,
#     #         patient_name TEXT NOT NULL,
#     #         doctor TEXT NOT NULL,
#     #         date TEXT NOT NULL,
#     #         time TEXT NOT NULL,
#     #         created_at TEXT NOT NULL
#     #     )
#     # """)

#     # =================================================
#     # ✅ NEW APPOINTMENTS TABLE WITH SLOT LOCKING
#     # =================================================
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS appointments (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             patient_name TEXT NOT NULL,
#             doctor TEXT NOT NULL,
#             date TEXT NOT NULL,
#             time TEXT NOT NULL,
#             created_at TEXT NOT NULL,
#             UNIQUE (doctor, date, time)
#         )
#     """)

#     # =================================================
#     # DOCTORS TABLE (UNCHANGED)
#     # =================================================
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS doctors (
#             doctor_id TEXT PRIMARY KEY,
#             name TEXT NOT NULL,
#             specialty TEXT NOT NULL,
#             area TEXT NOT NULL
#         )
#     """)

#     # =================================================
#     # DOCTOR SCHEDULE TABLE (UNCHANGED)
#     # =================================================
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS doctor_schedule (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             doctor_id TEXT NOT NULL,
#             day TEXT NOT NULL,
#             time TEXT NOT NULL,
#             FOREIGN KEY (doctor_id) REFERENCES doctors (doctor_id),
#             UNIQUE (doctor_id, day, time)
#         )
#     """)

#     conn.commit()
#     conn.close()
#     seed_doctor_catalog()

# # =================================================
# # INSERT HELPERS (UNCHANGED)
# # =================================================
# def add_doctor(doctor_id, name, specialty, area):
#     conn = get_connection()
#     cursor = conn.cursor()
#     cursor.execute("""
#         INSERT OR IGNORE INTO doctors (doctor_id, name, specialty, area)
#         VALUES (?, ?, ?, ?)
#     """, (doctor_id, name, specialty, area))
#     conn.commit()
#     conn.close()

# def add_doctor_schedule(doctor_id, day, time):
#     conn = get_connection()
#     cursor = conn.cursor()
#     cursor.execute("""
#         INSERT OR IGNORE INTO doctor_schedule (doctor_id, day, time)
#         VALUES (?, ?, ?)
#     """, (doctor_id, day, time))
#     conn.commit()
#     conn.close()

# # =================================================
# # SEED DATA (UNCHANGED)
# # =================================================
# def seed_doctor_catalog():
#     for doctor in DOCTOR_CATALOG:
#         add_doctor(
#             doctor_id=str(doctor["doctor_id"]),
#             name=doctor["name"],
#             specialty=doctor["specialty"],
#             area=doctor["area"]
#         )
#         for day, slots in doctor["schedule"].items():
#             for slot in slots:
#                 add_doctor_schedule(
#                     doctor_id=str(doctor["doctor_id"]),
#                     day=day,
#                     time=slot
#                 )

# # =================================================
# # QUERY HELPERS
# # =================================================
# def get_doctors_by_area_and_specialty(area: str, specialty: str):
#     conn = get_connection()
#     cursor = conn.cursor()
#     cursor.execute("""
#         SELECT d.doctor_id, d.name, d.specialty, s.day, s.time
#         FROM doctors d
#         JOIN doctor_schedule s ON d.doctor_id = s.doctor_id
#         WHERE d.area = ? AND d.specialty = ?
#         ORDER BY d.name, s.day
#     """, (area.lower(), specialty.lower()))
#     rows = cursor.fetchall()
#     conn.close()
#     return rows

# # =================================================
# # ✅ NEW: SPECIALTY EXISTENCE CHECK (UNCHANGED)
# # =================================================
# def specialty_exists_in_area(area: str, specialty: str) -> bool:
#     conn = get_connection()
#     cursor = conn.cursor()
#     cursor.execute("""
#         SELECT 1
#         FROM doctors
#         WHERE area = ? AND specialty = ?
#         LIMIT 1
#     """, (area.lower(), specialty.lower()))
#     exists = cursor.fetchone() is not None
#     conn.close()
#     return exists

# # =================================================
# # APPOINTMENT LOGIC (UNCHANGED)
# # =================================================
# def create_appointment(patient_name, doctor, date, time):
#     conn = get_connection()
#     cursor = conn.cursor()
#     try:
#         cursor.execute("""
#             INSERT INTO appointments (patient_name, doctor, date, time, created_at)
#             VALUES (?, ?, ?, ?, ?)
#         """, (
#             patient_name,
#             doctor,
#             date,
#             time,
#             datetime.utcnow().isoformat()
#         ))
#         conn.commit()
#     except sqlite3.IntegrityError:
#         conn.close()
#         raise
#     conn.close()

# def get_appointments():
#     conn = get_connection()
#     cursor = conn.cursor()
#     cursor.execute("SELECT * FROM appointments")
#     rows = cursor.fetchall()
#     conn.close()
#     return rows

# def is_slot_booked(doctor, date, time):
#     conn = get_connection()
#     cursor = conn.cursor()
#     cursor.execute("""
#         SELECT 1 FROM appointments
#         WHERE doctor = ? AND date = ? AND time = ?
#         LIMIT 1
#     """, (doctor, date, time))
#     exists = cursor.fetchone() is not None
#     conn.close()
#     return exists

# # =================================================
# # 🔧 MODIFICATION: FETCH BOOKED SLOTS FOR A DOCTOR & DAY
# # -------------------------------------------------
# # Purpose:
# # - Used BEFORE showing time slots to users
# # - Ensures already-booked slots are hidden
# # - Prevents poor UX where booking fails late
# # =================================================
# def get_booked_slots(doctor_name: str, day: str):
#     conn = get_connection()
#     cur = conn.cursor()

#     # ❌ OLD (NO SLOT VISIBILITY CONTROL)
#     # Booking validation happened only at insert time

#     # ✅ MODIFICATION: read already-booked slots
#     cur.execute(
#         """
#         SELECT time FROM appointments
#         WHERE doctor = ? AND date = ?
#         """,
#         (doctor_name, day)
#     )

#     rows = cur.fetchall()
#     conn.close()

#     # Return as set for fast lookup
#     return {row[0] for row in rows}














import sqlite3
from datetime import datetime
from pathlib import Path
import hashlib

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
    # ✅ USERS TABLE (NEW)
    # =================================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    # =================================================
    # ❌ OLD APPOINTMENTS TABLE (COMMENTED — DO NOT DELETE)
    # =================================================
    # patient_name, doctor, date, time, created_at

    # =================================================
    # ✅ APPOINTMENTS TABLE (EXTENDED, NON-BREAKING)
    # =================================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            patient_name TEXT NOT NULL,
            doctor TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            status TEXT DEFAULT 'booked',
            created_at TEXT NOT NULL,
            UNIQUE (doctor, date, time)
        )
    """)

    # =================================================
    # DOCTORS TABLE (UNCHANGED)
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
    # DOCTOR SCHEDULE TABLE (UNCHANGED)
    # =================================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS doctor_schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doctor_id TEXT NOT NULL,
            day TEXT NOT NULL,
            time TEXT NOT NULL,
            UNIQUE (doctor_id, day, time)
        )
    """)

    conn.commit()
    conn.close()
    seed_doctor_catalog()


# =================================================
# SYNTHETIC DOCTOR CATALOG DATA
# =================================================
DOCTOR_CATALOG = [
    {
        "doctor_id": 1,
        "name": "Dr. Ananya Sen",
        "specialty": "cardiology",
        "area": "salt lake",
        "schedule": {
            "Monday": ["10:00-11:00", "11:00-12:00"],
            "Thursday": ["15:00-17:00"]
        }
    },
    {
        "doctor_id": 2,
        "name": "Dr. Rakesh Malhotra",
        "specialty": "gastroenterology",
        "area": "salt lake",
        "schedule": {
            "Tuesday": ["09:00-10:00", "10:00-11:00"],
            "Friday": ["14:00-16:00"]
        }
    },
    {
        "doctor_id": 3,
        "name": "Dr. Nivedita Roy",
        "specialty": "neurology",
        "area": "ballygunge",
        "schedule": {
            "Monday": ["16:00-17:00"],
            "Wednesday": ["10:00-12:00"]
        }
    },
    {
        "doctor_id": 4,
        "name": "Dr. Arjun Mehta",
        "specialty": "general_physician",
        "area": "salt lake",
        "schedule": {
            "Monday": ["09:00-11:00"],
            "Wednesday": ["09:00-11:00"],
            "Saturday": ["10:00-12:00"]
        }
    },
    {
        "doctor_id": 5,
        "name": "Dr. Sneha Kapoor",
        "specialty": "dermatology",
        "area": "new town",
        "schedule": {
            "Tuesday": ["11:00-13:00"],
            "Thursday": ["10:00-12:00"]
        }
    },
    {
        "doctor_id": 6,
        "name": "Dr. Amit Chatterjee",
        "specialty": "orthopedics",
        "area": "new town",
        "schedule": {
            "Monday": ["14:00-16:00"],
            "Friday": ["09:00-11:00"]
        }
    },
    {
        "doctor_id": 7,
        "name": "Dr. Priya Mukherjee",
        "specialty": "gastroenterology",
        "area": "ballygunge",
        "schedule": {
            "Wednesday": ["13:00-15:00"],
            "Saturday": ["10:00-11:00"]
        }
    },
    {
        "doctor_id": 8,
        "name": "Dr. Kunal Verma",
        "specialty": "neurology",
        "area": "salt lake",
        "schedule": {
            "Tuesday": ["15:00-17:00"],
            "Friday": ["11:00-12:00"]
        }
    },
    {
        "doctor_id": 9,
        "name": "Dr. Sharmila Das",
        "specialty": "general_physician",
        "area": "new town",
        "schedule": {
            "Monday": ["08:00-10:00"],
            "Thursday": ["08:00-10:00"]
        }
    },
    {
        "doctor_id": 10,
        "name": "Dr. Vikram Sood",
        "specialty": "cardiology",
        "area": "ballygunge",
        "schedule": {
            "Tuesday": ["10:00-12:00"],
            "Saturday": ["11:00-13:00"]
        }
    }
]


# =================================================
# INSERT HELPERS
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
        INSERT OR IGNORE INTO doctor_schedule (doctor_id, day, time)
        VALUES (?, ?, ?)
    """, (doctor_id, day, time))
    conn.commit()
    conn.close()


# =================================================
# SEED DATA
# =================================================
def seed_doctor_catalog():
    for doctor in DOCTOR_CATALOG:
        add_doctor(
            doctor_id=str(doctor["doctor_id"]),
            name=doctor["name"],
            specialty=doctor["specialty"],
            area=doctor["area"]
        )
        for day, slots in doctor["schedule"].items():
            for slot in slots:
                add_doctor_schedule(
                    doctor_id=str(doctor["doctor_id"]),
                    day=day,
                    time=slot
                )


# =================================================
# PASSWORD HELPERS
# =================================================
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


# =================================================
# USER HELPERS (NEW)
# =================================================
def create_user(email: str, password: str):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO users (email, password_hash, created_at)
            VALUES (?, ?, ?)
        """, (email, hash_password(password), datetime.utcnow().isoformat()))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return None
    conn.close()
    return get_user_by_email(email)


def get_user_by_email(email: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, email FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()
    return row


def authenticate_user(email: str, password: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, password_hash FROM users WHERE email = ?
    """, (email,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    if row[1] != hash_password(password):
        return None
    return row[0]


# =================================================
# APPOINTMENT HELPERS (EXTENDED)
# =================================================
def create_appointment(patient_name, doctor, date, time, user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO appointments
        (user_id, patient_name, doctor, date, time, status, created_at)
        VALUES (?, ?, ?, ?, ?, 'booked', ?)
    """, (user_id, patient_name, doctor, date, time, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()


def get_user_appointments(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, doctor, date, time, status
        FROM appointments
        WHERE user_id = ?
        ORDER BY created_at DESC
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows


def cancel_appointment_db(appointment_id: int, user_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE appointments
        SET status = 'cancelled'
        WHERE id = ? AND user_id = ? AND status = 'booked'
    """, (appointment_id, user_id))
    conn.commit()
    updated = cursor.rowcount
    conn.close()
    return updated > 0


# =================================================
# SLOT HELPERS (UNCHANGED)
# =================================================
def is_slot_booked(doctor, date, time):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 1 FROM appointments
        WHERE doctor = ? AND date = ? AND time = ? AND status = 'booked'
    """, (doctor, date, time))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists


def get_booked_slots(doctor_name: str, day: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT time FROM appointments
        WHERE doctor = ? AND date = ? AND status = 'booked'
    """, (doctor_name, day))
    rows = cur.fetchall()
    conn.close()
    return {row[0] for row in rows}

# =================================================
# 🔁 LEGACY HELPER (DO NOT DELETE)
# -------------------------------------------------
# Purpose:
# - Keeps old routes / services working
# - Used ONLY by legacy list_appointments()
# =================================================
def get_appointments():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, patient_name, doctor, date, time, status, created_at
        FROM appointments
        ORDER BY created_at DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows

# =================================================
# 🔁 LEGACY DOCTOR QUERY (DO NOT DELETE)
# -------------------------------------------------
# Purpose:
# - Used by catalog_service
# - Area + specialty based doctor lookup
# - Date-agnostic by design (IMPORTANT)
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
# 🔁 LEGACY SPECIALTY CHECK (DO NOT DELETE)
# -------------------------------------------------
# Purpose:
# - Used by catalog_service
# - Checks if a specialty exists in an area
# - Ignores slot availability (IMPORTANT)
# =================================================
def specialty_exists_in_area(area: str, specialty: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 1
        FROM doctors
        WHERE area = ? AND specialty = ?
        LIMIT 1
    """, (area.lower(), specialty.lower()))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists
