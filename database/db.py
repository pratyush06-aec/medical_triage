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
# # ✅ NEW: SPECIALTY EXISTENCE CHECK (MODIFICATION)
# # -------------------------------------------------
# # Purpose:
# # - Checks if a doctor of a given specialty exists
# #   in a given area (ignores slot availability)
# # - Prevents incorrect GP fallback
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
















import sqlite3
from datetime import datetime
from pathlib import Path

# =================================================
# ✅ SYNTHETIC DOCTOR CATALOG DATA (UNCHANGED)
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
    # ❌ OLD APPOINTMENTS TABLE (COMMENTED — DO NOT DELETE)
    # =================================================
    # cursor.execute("""
    #     CREATE TABLE IF NOT EXISTS appointments (
    #         id INTEGER PRIMARY KEY AUTOINCREMENT,
    #         patient_name TEXT NOT NULL,
    #         doctor TEXT NOT NULL,
    #         date TEXT NOT NULL,
    #         time TEXT NOT NULL,
    #         created_at TEXT NOT NULL
    #     )
    # """)

    # =================================================
    # ✅ NEW APPOINTMENTS TABLE WITH SLOT LOCKING
    # =================================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT NOT NULL,
            doctor TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
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
            FOREIGN KEY (doctor_id) REFERENCES doctors (doctor_id),
            UNIQUE (doctor_id, day, time)
        )
    """)

    conn.commit()
    conn.close()
    seed_doctor_catalog()

# =================================================
# INSERT HELPERS (UNCHANGED)
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
# SEED DATA (UNCHANGED)
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
# QUERY HELPERS
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
# ✅ NEW: SPECIALTY EXISTENCE CHECK (UNCHANGED)
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

# =================================================
# APPOINTMENT LOGIC (UNCHANGED)
# =================================================
def create_appointment(patient_name, doctor, date, time):
    conn = get_connection()
    cursor = conn.cursor()
    try:
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
    except sqlite3.IntegrityError:
        conn.close()
        raise
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

# =================================================
# 🔧 MODIFICATION: FETCH BOOKED SLOTS FOR A DOCTOR & DAY
# -------------------------------------------------
# Purpose:
# - Used BEFORE showing time slots to users
# - Ensures already-booked slots are hidden
# - Prevents poor UX where booking fails late
# =================================================
def get_booked_slots(doctor_name: str, day: str):
    conn = get_connection()
    cur = conn.cursor()

    # ❌ OLD (NO SLOT VISIBILITY CONTROL)
    # Booking validation happened only at insert time

    # ✅ MODIFICATION: read already-booked slots
    cur.execute(
        """
        SELECT time FROM appointments
        WHERE doctor = ? AND date = ?
        """,
        (doctor_name, day)
    )

    rows = cur.fetchall()
    conn.close()

    # Return as set for fast lookup
    return {row[0] for row in rows}
