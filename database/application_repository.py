import sqlite3


class ApplicationRepository:

    def __init__(self, db_path="career_os.db"):

        self.conn = sqlite3.connect(db_path)

        self.cursor = self.conn.cursor()

        

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