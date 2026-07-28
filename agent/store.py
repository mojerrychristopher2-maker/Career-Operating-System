import json, sqlite3
from datetime import UTC, datetime
from pathlib import Path

class Store:
    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path)
        self.db.row_factory = sqlite3.Row
        self.db.executescript('''
        create table if not exists jobs (
          id text primary key, title text not null, company text not null, url text,
          description text not null, status text not null default 'discovered',
          fit_score integer, ats_score integer, reasoning text, created_at text not null);
        create table if not exists applications (
          job_id text primary key, status text not null, resume_path text, cover_letter_path text,
          applied_at text, follow_up_at text, foreign key(job_id) references jobs(id));
        create table if not exists events (
          id integer primary key autoincrement, job_id text, kind text not null, detail text not null, created_at text not null);
        ''')
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
    def add_application(self, job_id, status, resume, letter):
        self.db.execute('insert or replace into applications values(?,?,?,?,?,?)',(job_id,status,str(resume),str(letter),None,None));self.db.commit()
