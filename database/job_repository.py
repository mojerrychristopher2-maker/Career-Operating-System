import sqlite3
from modules.discovery.job import Job


class JobRepository:

    def __init__(self, db_path="career_os.db"):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            title TEXT,

            company TEXT,

            location TEXT,

            url TEXT UNIQUE,

            description TEXT,

            source TEXT

        )
        """)

        self.conn.commit()

    def save(self, job: Job):

        self.cursor.execute("""

        INSERT OR IGNORE INTO jobs(

            title,
            company,
            location,
            url,
            description,
            source

        )

        VALUES(?,?,?,?,?,?)

        """,

        (

            job.title,
            job.company,
            job.location,
            job.url,
            job.description,
            job.source

        ))

        self.conn.commit()

    def get_all(self):

        self.cursor.execute(

            "SELECT title,company,location,url,description,source FROM jobs"

        )

        return self.cursor.fetchall()