import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "clinic.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

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

    conn.commit()
    conn.close()


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

