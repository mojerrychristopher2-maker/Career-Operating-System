import json, sqlite3
from datetime import UTC, datetime
from pathlib import Path

class Store:
    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path)
        self.db.row_factory = sqlite3.Row
        self.db.executescript("""
        create table if not exists jobs (

            id text primary key,

            title text,

            company text,

            location text,

            url text,

            description text,

            status text default 'discovered',

            score integer default 0,

            created_at text

        );

        create table if not exists applications (

            job_id text primary key,

            status text not null,

            resume_path text,

            cover_letter_path text,

            applied_at text,

            follow_up_at text,

            company text,

            job_title text,

            source text,

            resume_version text,

            last_updated text,

            foreign key(job_id) references jobs(id)

        );

        create table if not exists companies (

            name text primary key,

            industry text,

            headquarters text,

            company_size text,

            website text,

            linkedin text,

            careers_url text,

            notes text,

            created_at text,

            last_updated text

        );

        create table if not exists events (

            id integer primary key autoincrement,

            job_id text,

            kind text,

            detail text,

            created_at text,

            foreign key(job_id) references jobs(id)

        );
        """)

        self.db.commit()
    def now(self): return datetime.now(UTC).isoformat()
    def log(self, kind, detail, job_id=None):
        self.db.execute("insert into events(job_id,kind,detail,created_at) values(?,?,?,?)", (job_id,kind,detail,self.now())); self.db.commit()
    def upsert_job(self, job):
        self.db.execute('''insert into jobs(id,title,company,url,description,created_at)
          values(:id,:title,:company,:url,:description,:created_at)
          on conflict(id) do nothing''', {**job,"created_at":self.now()}); self.db.commit()
    def jobs(self, status="discovered"):
        return self.db.execute("select * from jobs where status=? order by created_at", (status,)).fetchall()
    def update_job(self, job_id, **values):
        columns=','.join(f'{key}=?' for key in values)
        self.db.execute(f'update jobs set {columns} where id=?', (*values.values(),job_id)); self.db.commit()
    def application_exists(self, job_id): return bool(self.db.execute('select 1 from applications where job_id=?',(job_id,)).fetchone())
    def applications(self):
        """
        Return all stored applications.
        """
        return self.db.execute(
            "select * from applications order by job_id"
        ).fetchall()
    def add_application(
        self,
        job_id,
        status,
        resume,
        letter,
        company="",
        job_title="",
        source="",
        resume_version="v1"
    ):

        self.db.execute(
        """
            insert or replace into applications (

                job_id,
                status,
                resume_path,
                cover_letter_path,
                applied_at,
                follow_up_at,
                company,
                job_title,
                source,
                resume_version,
                last_updated

            )

            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,

            (

                job_id,
                status,
                str(resume),
                str(letter),

                self.now(),
                None,

                company,
                job_title,
                source,
                resume_version,

                self.now()

            )

        )

        self.db.commit()

    def company_exists(self, name):

        return bool(

            self.db.execute(

                "select 1 from companies where name=?",

                (name,)

            ).fetchone()

        )


    def create_company(self, name):

        self.db.execute(

            """
            insert into companies(

                name,

                created_at,

                last_updated

            )

            values(?,?,?)

            """,

            (

                name,

                self.now(),

                self.now(),

            ),

        )

        self.db.commit()


    def update_company(self, name, **fields):

        if not fields:

            return

        fields["last_updated"] = self.now()

        columns = ",".join(f"{k}=?" for k in fields)

        values = list(fields.values())

        values.append(name)

        self.db.execute(

            f"update companies set {columns} where name=?",

            values,

        )

        self.db.commit()


    def get_company(self, name):

        return self.db.execute(

            "select * from companies where name=?",

            (name,)

        ).fetchone()


    def all_companies(self):

        return self.db.execute(

            "select * from companies order by name"

        ).fetchall()