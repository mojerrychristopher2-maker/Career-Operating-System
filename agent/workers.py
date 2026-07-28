import json, re
from datetime import timedelta
from pathlib import Path
from .llm import LLM
from modules.ranking.job_ranker import JobRanker
from modules.ranking.top_jobs_selector import TopJobsSelector
from modules.discovery.discovery_service import DiscoveryService
from modules.ranking.job_ranker import JobRanker
from modules.ranking.top_jobs_selector import TopJobsSelector
from modules.repository.job_repository import JobRepository

SYSTEM = '''You are Mojerry Career OS. Never fabricate or exaggerate qualifications, skills, degrees, certificates, job history, outcomes, or metrics. Every recommendation must state its evidence and uncertainty. Return only the requested format.'''

class CareerWorkers:
    def __init__(self, store, settings):

        self.store = store
        self.settings = settings
        self.llm = LLM()

        self.discovery = DiscoveryService()

        self.repository = JobRepository(store)
    
    def discover(self):
        """Ingest normalized jobs written by approved job-board/API connectors."""
        if not self.settings.inbox.exists(): return 0
        items=json.loads(self.settings.inbox.read_text(encoding="utf-8")); count=0
        for job in items:
            if not all(k in job for k in ("id","title","company","description")): continue
            job.setdefault("url",""); self.store.upsert_job(job); count+=1
        self.store.log("discovery",f"Ingested {count} jobs from approved connector inbox.")
        return count
    def analyse(self, job, profile):
        prompt=f'''PROFILE (truthful source):\n{json.dumps(profile)}\n\nJOB:\n{dict(job)}\n\nReturn JSON with integer fit_score (0-100), integer ats_score (0-100), decision (Apply, Maybe, Skip), reasoning (max 100 words), and keywords (array).'''
        raw=self.llm.ask(SYSTEM+"\nYou are the Job Intelligence and ATS agents.",prompt)
        match=re.search(r'\{.*\}',raw,re.S)
        if not match: raise ValueError("Model did not return JSON job analysis")
        result=json.loads(match.group()); result["fit_score"]=max(0,min(100,int(result["fit_score"]))); result["ats_score"]=max(0,min(100,int(result["ats_score"])))
        return result
    def documents(self, job, profile, analysis):
        context=f"PROFILE:\n{json.dumps(profile)}\n\nJOB:\n{dict(job)}\n\nANALYSIS:\n{json.dumps(analysis)}"
        resume=self.llm.ask(SYSTEM+"\nYou are the Resume Intelligence agent. Write a concise ATS-safe tailored resume in Markdown. Use only profile facts.",context)
        letter=self.llm.ask(SYSTEM+"\nYou are the Cover Letter agent. Write a specific, concise cover letter. Use only profile facts.",context)
        safe=re.sub(r'[^a-z0-9]+','-',f"{job['company']}-{job['title']}".lower()).strip('-')
        self.settings.output_dir.mkdir(parents=True,exist_ok=True)
        resume_path=self.settings.output_dir/f"{safe}-resume.md"; letter_path=self.settings.output_dir/f"{safe}-cover-letter.md"
        resume_path.write_text(resume,encoding='utf-8'); letter_path.write_text(letter,encoding='utf-8')
        return resume_path,letter_path
    def process(self, profile, jobs):

        if not jobs:
            return
        
        saved = self.repository.save_jobs(jobs)

        jobs = self.repository.discovered_jobs()

        ranker = JobRanker(profile)

        ranked_jobs = ranker.rank(jobs)

        selector = TopJobsSelector(top_n=3)

        selected_jobs = selector.select(ranked_jobs)

        for item in selected_jobs:

            job = item["job"]

            if not self.settings.openai_key:

                self.store.log(
                    "analysis",
                    "Skipped AI analysis because no OPENAI_API_KEY is configured.",
                    job["id"]
                )

                continue

            analysis = self.analyse(job, profile)

            self.store.update_job(
                job["id"],
                status=analysis["decision"].lower(),
                fit_score=analysis["fit_score"],
                ats_score=analysis["ats_score"],
                reasoning=analysis["reasoning"]
            )

            self.store.log(
                "analysis",
                analysis["reasoning"],
                job["id"]
            )

            if (
                analysis["decision"] == "Apply"
                and analysis["fit_score"] >= 80
            ):

                resume, letter = self.documents(
                    job,
                    profile,
                    analysis
                )

                status = "ready_for_submission"

                self.store.add_application(
                    job["id"],
                    status,
                    resume,
                    letter
                )

                self.store.log(
                    "documents",
                    f"Created truthful tailored documents; status: {status}.",
                    job["id"]
                )
