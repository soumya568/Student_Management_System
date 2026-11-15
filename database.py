
import sqlite3

def get_connection():
    return sqlite3.connect("students.db")

def create_table():
    conn = get_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            course TEXT NOT NULL,
            year INTEGER NOT NULL
        )
    """)

    conn.commit()
    conn.close()
