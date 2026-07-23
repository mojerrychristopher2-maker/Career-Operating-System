import sqlite3


class ApplicationRepository:

    def __init__(self, db_name="career_os.db"):

        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()

        self.create_table()

    def create_table(self):

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS applications (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                company TEXT,

                job_title TEXT,

                location TEXT,

                job_url TEXT,

                applied_date TEXT,

                status TEXT,

                resume_version TEXT,

                cover_letter_version TEXT
            )
        """)

        self.connection.commit()

    def save(self, application):

        self.cursor.execute("""
            INSERT INTO applications (

                company,
                job_title,
                location,
                job_url,
                applied_date,
                status,
                resume_version,
                cover_letter_version

            )

            VALUES (?, ?, ?, ?, ?, ?, ?, ?)

        """, (

            application["company"],
            application["job_title"],
            application["location"],
            application["job_url"],
            application["applied_date"],
            application["status"],
            application["resume_version"],
            application["cover_letter_version"]

        ))

        self.connection.commit()

    def exists(self, company, job_title, job_url):

        self.cursor.execute("""

            SELECT COUNT(*)

            FROM applications

            WHERE company = ?
            AND job_title = ?
            AND job_url = ?

        """, (company, job_title, job_url))

        return self.cursor.fetchone()[0] > 0
    
    def update_status(self, application_id, status):

        self.cursor.execute("""

            UPDATE applications

            SET status = ?

            WHERE id = ?

        """, (status, application_id))

        self.connection.commit()

    def get(self, application_id):

        self.cursor.execute("""

            SELECT *

            FROM applications

            WHERE id = ?

        """, (application_id,))

        return self.cursor.fetchone()

    def all(self):

        self.cursor.execute("""

            SELECT *

            FROM applications

            ORDER BY applied_date DESC

        """)

        return self.cursor.fetchall()