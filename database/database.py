import sqlite3
from pathlib import Path

DATABASE = Path("career_os.db")


def get_connection():
    """Create and return a database connection."""
    return sqlite3.connect(DATABASE)


def initialize_database():
    """Create database tables if they don't already exist."""

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jobs (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        title TEXT,

        company TEXT,

        location TEXT,

        url TEXT,

        description TEXT,

        match_score INTEGER,

        status TEXT
    )
    """)

    conn.commit()
    conn.close()

    print("Career OS database initialized successfully.")