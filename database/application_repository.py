from pathlib import Path
import sqlite3

from config.settings import APPLICATION_DIR


class ApplicationRepository:

    def __init__(self):

        APPLICATION_DIR.mkdir(

            parents=True,

            exist_ok=True

        )

        self.database = APPLICATION_DIR / "career_os.db"

        self.connection = sqlite3.connect(

            self.database

        )

        self.create_table()

    def create_table(self):

        cursor = self.connection.cursor()

        cursor.execute("""

        CREATE TABLE IF NOT EXISTS applications (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            company TEXT,

            title TEXT,

            score INTEGER,

            applied INTEGER

        )

        """)

        self.connection.commit()

    def save(self, company, title, score, applied):

        cursor = self.connection.cursor()

        cursor.execute(

            """

            INSERT INTO applications (

                company,

                title,

                score,

                applied

            )

            VALUES (?, ?, ?, ?)

            """,

            (

                company,

                title,

                score,

                applied

            )

        )

        self.connection.commit()
    
    def get_all(self):

        cursor = self.connection.cursor()

        cursor.execute("""

            SELECT *

            FROM applications

        """)

        return cursor.fetchall()
    
    def count(self):

        cursor = self.connection.cursor()

        cursor.execute("""

            SELECT COUNT(*)

            FROM applications

        """)

        return cursor.fetchone()[0]