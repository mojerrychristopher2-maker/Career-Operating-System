"""
MOJERRY CAREER OS — single-file autonomous career agent

Setup:
  1. Set OPENAI_API_KEY in your terminal environment.
  2. Create profile.json from the PROFILE_EXAMPLE below.
  3. Create jobs.json using the JOB_EXAMPLE format.
  4. Run: python mojerry_career_agent.py run-once
     Or:  python mojerry_career_agent.py watch

The agent only uses facts in profile.json. It stages documents for review and
does not log in to job sites or submit applications without a site connector.
"""
import argparse
import json
import os
import re
import sqlite3
import time
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "career_os.db"
PROFILE_PATH = ROOT / "profile.json"
JOBS_PATH = ROOT / "jobs.json"
ARTIFACTS = ROOT / "artifacts"
MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
POLL_SECONDS = int(os.getenv("POLL_SECONDS", "1800"))

PROFILE_EXAMPLE = {
    "name": "Mojerry",
    "headline": "Data Analyst",
    "target_roles": ["Data Analyst", "Business Intelligence Analyst"],
    "skills": ["SQL", "Power BI", "Python", "Excel"],
    "experience": ["Add only real roles, projects, outcomes, and achievements here."],
    "education_and_certifications": []
}
JOB_EXAMPLE = [{
    "id": "unique-job-id", "title": "Business Intelligence Analyst",
    "company": "Example Company", "url": "https://company.example/jobs/123",
    "description": "Paste the complete job description here."
}]

SYSTEM_RULES = """You are Mojerry Career OS, an autonomous recruiter and career agent.
Never invent, exaggerate, or infer qualifications, degrees, certifications, skills,
employment, projects, dates, metrics, or achievements. Use only facts in the
provided profile. Explain recommendations with evidence. Return only the format asked."""

def now(): return datetime.now(UTC).isoformat()

def database():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    db.executescript("""
      create table if not exists jobs (
        id text primary key, title text, company text, url text, description text,
        status text default 'discovered', fit_score integer, ats_score integer,
        reasoning text, created_at text);
      create table if not exists applications (
        job_id text primary key, status text, resume_path text, cover_letter_path text,
        prepared_at text, follow_up_at text);
      create table if not exists events (
        id integer primary key autoincrement, job_id text, kind text, detail text, created_at text);
    """)
    db.commit()
    return db

def log(db, kind, detail, job_id=None):
    db.execute("insert into events(job_id,kind,detail,created_at) values(?,?,?,?)",
               (job_id, kind, detail, now()))
    db.commit()

def load_profile():
    if not PROFILE_PATH.exists():
        PROFILE_PATH.write_text(json.dumps(PROFILE_EXAMPLE, indent=2), encoding="utf-8")
        raise RuntimeError("profile.json was created. Fill it with verified facts, then run again.")
    return json.loads(PROFILE_PATH.read_text(encoding="utf-8"))

def ask_ai(instructions, prompt):
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("Set OPENAI_API_KEY before running the AI agent.")
    payload = json.dumps({"model": MODEL, "instructions": instructions, "input": prompt}).encode()
    request = urllib.request.Request(
        "https://api.openai.com/v1/responses", data=payload,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    )
    with urllib.request.urlopen(request, timeout=90) as response:
        data = json.load(response)
    return data["output"][0]["content"][0]["text"]

def ingest_jobs(db):
    if not JOBS_PATH.exists():
        JOBS_PATH.write_text(json.dumps(JOB_EXAMPLE, indent=2), encoding="utf-8")
        print("jobs.json was created. Paste approved job listings into it, then run again.")
        return 0
    jobs = json.loads(JOBS_PATH.read_text(encoding="utf-8"))
    count = 0
    for job in jobs:
        required = {"id", "title", "company", "description"}
        if not required.issubset(job):
            print(f"Skipped invalid job: {job}")
            continue
        db.execute("""insert into jobs(id,title,company,url,description,created_at)
           values(?,?,?,?,?,?) on conflict(id) do nothing""",
           (job["id"], job["title"], job["company"], job.get("url", ""), job["description"], now()))
        count += 1
    db.commit(); log(db, "discovery", f"Read {count} job records from jobs.json.")
    return count

def analyze_job(job, profile):
    prompt = f"""TRUTHFUL PROFILE:\n{json.dumps(profile)}\n\nJOB:\n{dict(job)}

Return strict JSON only:
{{"fit_score": 0, "ats_score": 0, "decision": "Apply|Maybe|Skip",
"reasoning": "brief explainable evidence", "keywords": ["keyword"]}}"""
    response = ask_ai(SYSTEM_RULES + "\nAct as Job Intelligence and ATS Optimization agents.", prompt)
    found = re.search(r"\{.*\}", response, re.S)
    if not found: raise ValueError("AI analysis was not valid JSON")
    result = json.loads(found.group())
    result["fit_score"] = max(0, min(100, int(result["fit_score"])))
    result["ats_score"] = max(0, min(100, int(result["ats_score"])))
    if result["decision"] not in ("Apply", "Maybe", "Skip"): result["decision"] = "Maybe"
    return result

def create_documents(job, profile, analysis):
    context = f"PROFILE:\n{json.dumps(profile)}\n\nJOB:\n{dict(job)}\n\nANALYSIS:\n{json.dumps(analysis)}"
    resume = ask_ai(SYSTEM_RULES + "\nAct as Resume Intelligence Agent. Write an ATS-friendly tailored resume in Markdown, using only profile facts.", context)
    letter = ask_ai(SYSTEM_RULES + "\nAct as Cover Letter Agent. Write a concise unique cover letter using only profile facts.", context)
    ARTIFACTS.mkdir(exist_ok=True)
    slug = re.sub(r"[^a-z0-9]+", "-", f"{job['company']}-{job['title']}".lower()).strip("-")
    resume_file, letter_file = ARTIFACTS / f"{slug}-resume.md", ARTIFACTS / f"{slug}-cover-letter.md"
    resume_file.write_text(resume, encoding="utf-8")
    letter_file.write_text(letter, encoding="utf-8")
    return resume_file, letter_file

def run_cycle():
    db = database()
    profile = load_profile()
    print(f"Discovery: {ingest_jobs(db)} records checked.")
    pending = db.execute("select * from jobs where status='discovered'").fetchall()
    for job in pending:
        print(f"Analysing: {job['title']} at {job['company']}")
        analysis = analyze_job(job, profile)
        db.execute("update jobs set status=?,fit_score=?,ats_score=?,reasoning=? where id=?",
                   (analysis["decision"].lower(), analysis["fit_score"], analysis["ats_score"], analysis["reasoning"], job["id"]))
        db.commit(); log(db, "analysis", analysis["reasoning"], job["id"])
        if analysis["decision"] == "Apply" and analysis["fit_score"] >= 80:
            resume, letter = create_documents(job, profile, analysis)
            db.execute("insert or replace into applications values(?,?,?,?,?,?)",
                       (job["id"], "ready_for_submission", str(resume), str(letter), now(), None))
            db.commit(); log(db, "documents", "Created truthful tailored documents; queued for authorized submission.", job["id"])
            print(f"  Prepared: {resume.name}, {letter.name}")
        else:
            print(f"  {analysis['decision']}: {analysis['reasoning']}")
    log(db, "cycle", "Autonomous cycle completed.")
    db.close()

def show_status():
    db = database()
    for row in db.execute("select status, count(*) as count from jobs group by status"):
        print(f"{row['status']}: {row['count']}")
    db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mojerry Career OS")
    parser.add_argument("command", choices=["run-once", "watch", "status"])
    command = parser.parse_args().command
    if command == "status": show_status()
    elif command == "run-once": run_cycle()
    else:
        while True:
            try: run_cycle()
            except Exception as error: print(f"Cycle failed: {error}")
            time.sleep(POLL_SECONDS)
