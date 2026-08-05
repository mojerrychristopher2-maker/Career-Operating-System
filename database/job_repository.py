import sqlite3


class JobRepository:

    def __init__(self, db_path="career_os.db"):

        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def save(self, job):

        self.cursor.execute(
            """
            INSERT OR IGNORE INTO jobs
            (
                title,
                company,
                location,
                url,
                description,
                match_score,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                job.get("title"),
                job.get("company"),
                job.get("location"),
                job.get("url"),
                job.get("page_text"),
                job.get("filter_score", 0),
                "Discovered"
            )
        )

        self.conn.commit()

    def update_status(self, url, status):

        self.cursor.execute(
            """
            UPDATE jobs
            SET status = ?
            WHERE url = ?
            """,
            (
                status,
                url
            )
        )

        self.conn.commit()

    def get_by_url(self, url):

        self.cursor.execute(
            """
            SELECT *
            FROM jobs
            WHERE url = ?
            """,
            (url,)
        )

        return self.cursor.fetchone()

    def get_all(self):

        self.cursor.execute(
            """
            SELECT *
            FROM jobs
            ORDER BY match_score DESC
            """
        )

        return self.cursor.fetchall()

    def top_matches(self, limit=20):

        self.cursor.execute(
            """
            SELECT *
            FROM jobs
            ORDER BY match_score DESC
            LIMIT ?
            """,
            (limit,)
        )

        return self.cursor.fetchall()

    def search_company(self, company):

        self.cursor.execute(
            """
            SELECT *
            FROM jobs
            WHERE company LIKE ?
            """,
            (f"%{company}%",)
        )

        return self.cursor.fetchall()

    def search_title(self, title):

        self.cursor.execute(
            """
            SELECT *
            FROM jobs
            WHERE title LIKE ?
            """,
            (f"%{title}%",)
        )

        return self.cursor.fetchall()