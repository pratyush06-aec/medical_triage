import sqlite3

DB_PATH = "clinic.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    db = get_db()
    db.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT,
            doctor_name TEXT,
            date TEXT,
            time TEXT
        )
    """)
    db.commit()
    db.close()

if __name__ == "__main__":
    init_db()