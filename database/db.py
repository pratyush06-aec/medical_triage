import sqlite3
from datetime import datetime
from pathlib import Path
import hashlib
import os

# =================================================
# 🧩 SCHEMA VERSIONING
# =================================================
CURRENT_SCHEMA_VERSION = 2


# =================================================
# 📁 DATABASE FILE (ENV-BASED)
# =================================================
BASE_DIR = Path(__file__).resolve().parent.parent

ENV = os.getenv("APP_ENV", "dev")

if ENV == "prod":
    DB_PATH = BASE_DIR / "database" / "clinic_prod.db"
else:
    DB_PATH = BASE_DIR / "database" / "clinic_dev.db"

# ❌ OLD (HARDCODED DB — COMMENTED, NOT DELETED)
# DB_PATH = BASE_DIR / "database" / "clinic.db"

DB_PATH.parent.mkdir(parents=True, exist_ok=True)
print("🟢 USING DATABASE:", DB_PATH)


# =================================================
# 🔌 CONNECTION (SINGLE SOURCE OF TRUTH)
# =================================================
def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


# =================================================
# 🔧 NORMALIZATION HELPER  (MODIFICATION)
# =================================================
# 🔧 MODIFICATION START
def normalize(text: str) -> str:
    """
    Normalizes human / LLM input to DB-safe tokens.
    'Salt Lake' -> 'salt_lake'
    'Cardiologist ' -> 'cardiologist'
    """
    return (
        text.strip()
            .lower()
            .replace(" ", "_")
    )
# 🔧 MODIFICATION END


# =================================================
# 🧩 SCHEMA VERSION HELPERS
# =================================================
def get_schema_version(cursor):
    try:
        cursor.execute("SELECT version FROM schema_version LIMIT 1")
        row = cursor.fetchone()
        return row[0] if row else None
    except sqlite3.OperationalError:
        # schema_version table does not exist yet
        return None


def upgrade_schema(cursor, from_version):
    cursor.execute(
        "UPDATE schema_version SET version = ?",
        (CURRENT_SCHEMA_VERSION,)
    )


# =================================================
# 🧱 INITIALIZATION (STRUCTURE ONLY, NO DATA LOSS)
# =================================================
def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    patient_name TEXT NOT NULL,
    doctor TEXT NOT NULL,
    date TEXT NOT NULL,
    time TEXT NOT NULL,
    status TEXT DEFAULT 'booked',
    created_at TEXT NOT NULL
)""")


    current_version = get_schema_version(cursor) or 0

    if current_version == 0:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER NOT NULL
            )
        """)
        cursor.execute("DELETE FROM schema_version")
        cursor.execute(
            "INSERT INTO schema_version (version) VALUES (?)",
            (CURRENT_SCHEMA_VERSION,)
        )

    elif current_version < CURRENT_SCHEMA_VERSION:
        upgrade_schema(cursor, current_version)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            patient_name TEXT NOT NULL,
            doctor TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            status TEXT DEFAULT 'booked',
            created_at TEXT NOT NULL,
            UNIQUE (doctor, date, time)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS doctors (
            doctor_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            specialty TEXT NOT NULL,
            area TEXT NOT NULL
        )
    """)

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
# 🔐 AUTH HELPERS
# =================================================
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def create_user(email: str, password: str):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (email, password_hash, created_at) VALUES (?, ?, ?)",
            (email, hash_password(password), datetime.utcnow().isoformat())
        )
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
    cursor.execute(
        "SELECT id, password_hash FROM users WHERE email = ?",
        (email,)
    )
    row = cursor.fetchone()
    conn.close()
    if not row or row[1] != hash_password(password):
        return None
    return row[0]


# =================================================
# 🩺 DOCTOR HELPERS
# =================================================
def add_doctor(doctor_id, name, specialty, area):
    conn = get_connection()
    cursor = conn.cursor()

    # 🔧 MODIFICATION: normalize before storing
    cursor.execute(
        "INSERT OR IGNORE INTO doctors VALUES (?, ?, ?, ?)",
        (
            doctor_id,
            name,
            normalize(specialty),
            normalize(area)
        )
    )

    conn.commit()
    conn.close()


def add_doctor_schedule(doctor_id, day, time):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR IGNORE INTO doctor_schedule (doctor_id, day, time) VALUES (?, ?, ?)",
        (doctor_id, day, time)
    )
    conn.commit()
    conn.close()


# =================================================
# 🔧 DOCTOR LOOKUP (NORMALIZED)  (MODIFICATION)
# =================================================
def get_doctors_by_area_and_specialty(area: str, specialty: str):
    # 🔧 MODIFICATION START
    area_n = normalize(area)
    specialty_n = normalize(specialty)
    # 🔧 MODIFICATION END

    conn = get_connection()
    cursor = conn.cursor()

    # ❌ OLD (NON-NORMALIZED — COMMENTED)
    # cursor.execute(
    #     "... WHERE d.area = ? AND d.specialty = ?",
    #     (area.lower(), specialty.lower())
    # )

    cursor.execute("""
        SELECT d.doctor_id, d.name, d.specialty, s.day, s.time
        FROM doctors d
        JOIN doctor_schedule s ON d.doctor_id = s.doctor_id
        WHERE d.area = ? AND d.specialty = ?
    """, (area_n, specialty_n))

    rows = cursor.fetchall()
    conn.close()
    return rows


# =================================================
# 🔧 SPECIALTY EXISTENCE CHECK (NORMALIZED)  (MODIFICATION)
# =================================================
def specialty_exists_in_area(area: str, specialty: str) -> bool:
    # 🔧 MODIFICATION START
    area_n = normalize(area)
    specialty_n = normalize(specialty)
    # 🔧 MODIFICATION END

    conn = get_connection()
    cursor = conn.cursor()

    # ❌ OLD (COMMENTED)
    # cursor.execute(
    #     "SELECT 1 FROM doctors WHERE area = ? AND specialty = ? LIMIT 1",
    #     (area.lower(), specialty.lower())
    # )

    # ✅ NEW (NORMALIZED QUERY)
    cursor.execute(
        "SELECT 1 FROM doctors WHERE area = ? AND specialty = ? LIMIT 1",
        (area_n, specialty_n)
    )

    exists = cursor.fetchone() is not None
    conn.close()
    return exists


# =================================================
# 📅 APPOINTMENTS
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


def book_appointment_with_user(user_id, data: dict):
    if is_slot_booked(data["doctor"], data["date"], data["time"]):
        return False, "Slot already booked"

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO appointments
        (user_id, patient_name, doctor, date, time, status, created_at)
        VALUES (?, ?, ?, ?, ?, 'booked', ?)
    """, (
        user_id,
        data["patient_name"],
        data["doctor"],
        data["date"],
        data["time"],
        datetime.utcnow().isoformat()
    ))
    conn.commit()
    conn.close()
    return True, "Appointment booked successfully"


# =================================================
# ❌ CANCEL APPOINTMENT (FINAL, SAFE)
# =================================================
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
# 🌱 FULL DOCTOR CATALOG (SOURCE OF TRUTH)
# =================================================
DOCTOR_CATALOG = [
    {
        "doctor_id": 1,
        "name": "Dr. Ananya Sen",
        "specialty": "cardiologist",
        "area": "salt lake",
        "schedule": {
            "Monday": ["10:00-11:00", "11:00-12:00"],
            "Thursday": ["15:00-17:00"]
        }
    },
    {
        "doctor_id": 2,
        "name": "Dr. Rakesh Malhotra",
        "specialty": "gastroenterologist",
        "area": "salt lake",
        "schedule": {
            "Tuesday": ["09:00-10:00", "10:00-11:00"],
            "Friday": ["14:00-16:00"]
        }
    },
    {
        "doctor_id": 3,
        "name": "Dr. Nivedita Roy",
        "specialty": "neurologist",
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
        "name": "Dr. Suman Chatterjee",
        "specialty": "cardiologist",
        "area": "new town",
        "schedule": {
            "Tuesday": ["11:00-12:00"],
            "Friday": ["10:00-12:00"]
        }
    },
    {
        "doctor_id": 6,
        "name": "Dr. Priya Mukherjee",
        "specialty": "gastroenterologist",
        "area": "new town",
        "schedule": {
            "Monday": ["14:00-16:00"],
            "Thursday": ["10:00-11:00"]
        }
    },
    {
        "doctor_id": 7,
        "name": "Dr. Amitava Das",
        "specialty": "neurologist",
        "area": "sealdah",
        "schedule": {
            "Wednesday": ["11:00-13:00"],
            "Saturday": ["09:00-10:00"]
        }
    },
    {
        "doctor_id": 8,
        "name": "Dr. Rina Banerjee",
        "specialty": "general_physician",
        "area": "sealdah",
        "schedule": {
            "Monday": ["10:00-12:00"],
            "Friday": ["09:00-11:00"]
        }
    },
    {
        "doctor_id": 9,
        "name": "Dr. Kunal Ghosh",
        "specialty": "cardiologist",
        "area": "dum dum",
        "schedule": {
            "Tuesday": ["15:00-17:00"],
            "Thursday": ["11:00-12:00"]
        }
    },
    {
        "doctor_id": 10,
        "name": "Dr. Sohini Paul",
        "specialty": "gastroenterologist",
        "area": "dum dum",
        "schedule": {
            "Wednesday": ["09:00-11:00"],
            "Saturday": ["11:00-12:00"]
        }
    },
    {
        "doctor_id": 11,
        "name": "Dr. Debashis Roy",
        "specialty": "neurologist",
        "area": "howrah",
        "schedule": {
            "Monday": ["15:00-17:00"],
            "Friday": ["10:00-11:00"]
        }
    },
    {
        "doctor_id": 12,
        "name": "Dr. Tanima Sen",
        "specialty": "general_physician",
        "area": "howrah",
        "schedule": {
            "Tuesday": ["09:00-11:00"],
            "Thursday": ["14:00-15:00"]
        }
    },
    {
        "doctor_id": 13,
        "name": "Dr. Anirban Bose",
        "specialty": "cardiologist",
        "area": "behala",
        "schedule": {
            "Wednesday": ["10:00-12:00"],
            "Saturday": ["14:00-15:00"]
        }
    },
    {
        "doctor_id": 14,
        "name": "Dr. Moumita Dey",
        "specialty": "general_physician",
        "area": "behala",
        "schedule": {
            "Monday": ["09:00-10:00"],
            "Friday": ["16:00-17:00"]
        }
    }
]

# ❌ OLD DUPLICATE CATALOG (COMMENTED — DO NOT DELETE)
# DOCTOR_CATALOG = []


def seed_doctor_catalog():
    for doctor in DOCTOR_CATALOG:
        add_doctor(
            str(doctor["doctor_id"]),
            doctor["name"],
            doctor["specialty"],
            doctor["area"]
        )
        for day, slots in doctor["schedule"].items():
            for slot in slots:
                add_doctor_schedule(str(doctor["doctor_id"]), day, slot)


# =================================================
# 🔁 LEGACY COMPATIBILITY — REQUIRED BY booking_service
# =================================================
# 🔧 MODIFICATION START
def create_appointment(patient_name, doctor, date, time, user_id=None):
    """
    Legacy helper required by booking_service.
    Internally forwards to book_appointment_with_user.
    DO NOT DELETE.
    """
    data = {
        "patient_name": patient_name,
        "doctor": doctor,
        "date": date,
        "time": time
    }
    return book_appointment_with_user(user_id, data)
# 🔧 MODIFICATION END

def get_appointments():
    """
    Legacy helper required by booking_service.
    Returns all appointments (admin / legacy use).
    DO NOT DELETE.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, patient_name, doctor, date, time, status
        FROM appointments
        ORDER BY created_at DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_booked_slots(doctor_name: str, date: str):
    """
    Legacy helper required by booking_service.
    Returns a set of booked time slots for a doctor on a given date.
    DO NOT DELETE.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT time FROM appointments
        WHERE doctor = ? AND date = ? AND status = 'booked'
    """, (doctor_name, date))
    rows = cursor.fetchall()
    conn.close()
    return {row[0] for row in rows}

def get_appointments_by_patient(patient_name: str):
    """
    Legacy helper required by booking_service.
    Returns appointments for a patient name.
    DO NOT DELETE.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, patient_name, doctor, date, time, status
        FROM appointments
        WHERE patient_name = ?
        ORDER BY created_at DESC
    """, (patient_name,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_appointment(appointment_id: int, user_id: int | None = None):
    """
    Legacy helper required by booking_service.
    Forwards to safe cancel logic.
    DO NOT DELETE.
    """
    if user_id is not None:
        return cancel_appointment_db(appointment_id, user_id)

    # legacy fallback (no user context)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE appointments
        SET status = 'cancelled'
        WHERE id = ?
    """, (appointment_id,))
    conn.commit()
    updated = cursor.rowcount
    conn.close()
    return updated > 0

def get_user_appointments(user_id: int):
    """
    Legacy helper required by profile_service.
    Returns all appointments for a user.
    DO NOT DELETE.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT *
    FROM appointments
    WHERE user_id = ?
    AND status = 'booked'
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

