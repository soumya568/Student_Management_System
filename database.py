
import os
import psycopg

def get_connection():
    return psycopg.connect(os.environ["DATABASE_URL"])

def create_table():
    conn = get_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            course TEXT NOT NULL,
            year INTEGER NOT NULL
        )
    """)

    conn.commit()
    conn.close()
