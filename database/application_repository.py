import sqlite3
from datetime import datetime


class ApplicationRepository:

    def __init__(self, db_path="career_os.db"):

        self.conn = sqlite3.connect(db_path)

        self.cursor = self.conn.cursor()

        self._create_tables()

    def _create_tables(self):

        self.cursor.execute("""
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

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS discovered_jobs (

                url TEXT PRIMARY KEY,

                title TEXT,

                company TEXT,

                first_seen TEXT,

                last_seen TEXT,

                status TEXT

            )
        """)

        self.conn.commit()

    def save(self, company, title, url, applied_date, status):

        self.cursor.execute("""

        INSERT OR IGNORE INTO applications(

            company,
            title,
            url,
            applied_date,
            status,
            notes

        )

        VALUES(?,?,?,?,?,?)

        """,

        (

            company,
            title,
            url,
            applied_date,
            status,
            ""

        ))

        self.conn.commit()

    def update_status(self, url, status):

        self.cursor.execute("""

        UPDATE applications

        SET status=?

        WHERE url=?

        """,

        (

            status,
            url

        ))

        self.conn.commit()

    def get_all(self):

        self.cursor.execute("""

        SELECT

            company,
            title,
            status,
            applied_date

        FROM applications

        """)

        return self.cursor.fetchall()

    def has_seen(self, url):

        cursor = self.conn.execute(

            "SELECT 1 FROM discovered_jobs WHERE url=?",

            (url,)

        )

        return cursor.fetchone() is not None

    def remember_job(self, job):

        now = datetime.now().isoformat()

        self.conn.execute("""

        INSERT OR REPLACE INTO discovered_jobs (

            url,

            title,

            company,

            first_seen,

            last_seen,

            status

        )

        VALUES (

            ?, ?, ?,

            COALESCE(

                (SELECT first_seen

                FROM discovered_jobs

                WHERE url=?),

                ?

            ),

            ?,

            ?

        )

        """,

        (

            job["url"],

            job["title"],

            job.get("company", ""),

            job["url"],

            now,

            now,

            "DISCOVERED"

        )

        )

        self.conn.commit()