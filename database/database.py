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

    # ==========================
    # Jobs
    # ==========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jobs (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        title TEXT,
        company TEXT,
        location TEXT,
        url TEXT UNIQUE,
        description TEXT,

        match_score INTEGER,
        status TEXT,

        discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # ==========================
    # Applications
    # ==========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS applications (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        company TEXT,

        title TEXT,

        url TEXT UNIQUE,

        applied_date TEXT,

        status TEXT,

        notes TEXT

    )
    """)

    # ==========================
    # Companies
    # ==========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS companies (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        name TEXT UNIQUE,

        website TEXT,

        careers_url TEXT,

        industry TEXT
    )
    """)

    # ==========================
    # Recruiters
    # ==========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS recruiters (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        company_id INTEGER,

        name TEXT,

        email TEXT,

        linkedin TEXT,

        FOREIGN KEY(company_id)
            REFERENCES companies(id)
    )
    """)

    # ==========================
    # Interviews
    # ==========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS interviews (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        application_id INTEGER,

        interview_date TEXT,

        interview_type TEXT,

        outcome TEXT,

        notes TEXT,

        FOREIGN KEY(application_id)
            REFERENCES applications(id)
    )
    """)

    # ==========================
    # Skills to Learn
    # ==========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS learning_queue (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        skill TEXT,

        source_job TEXT,

        priority INTEGER,

        learned INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()

    print("Career OS database initialized successfully.")