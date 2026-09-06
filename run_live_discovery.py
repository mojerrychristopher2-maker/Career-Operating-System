import sys
sys.path.insert(0, r"C:\Users\mojer\Documents\Codex\2026-07-20\bui\outputs\mojerry-career-os")

from core.profile_manager import ProfileManager
from modules.discovery.discovery_agent import DiscoveryAgent
from modules.ranking.job_ranker import JobRanker
from datetime import datetime
from modules.builder.resume_tailor import ResumeTailor
from modules.cover_letter.cover_letter_engine import CoverLetterEngine
from database.application_repository import ApplicationRepository
from database.job_repository import JobRepository
from modules.intelligence.decision_engine import DecisionEngine
from modules.documents.resume_writer import ResumeWriter
from modules.documents.cover_letter_writer import CoverLetterWriter
from modules.integration import n8n_events
from database.application_intelligence import ApplicationIntelligence
from modules.intelligence.opportunity_intelligence import OpportunityIntelligence

def run():
    print("Initializing Career OS pipeline...")
    profile = ProfileManager().get_all()
    agent = DiscoveryAgent()
    ranker = JobRanker(profile)
    
    print("Starting discovery...")
    jobs = agent.discover_jobs()
    print(f"Total jobs discovered: {len(jobs)}")
    
    print("Ranking jobs...")
    ranked = ranker.rank(jobs)
    print(f"Total jobs eligible for ranking: {len(ranked)}")
    
    # Analyze
    rejected = [j for j in ranked if j['score'] == 0]
    eligible = [j for j in ranked if j['score'] > 0]
    
    print(f"Jobs rejected by alignment gate: {len(rejected)}")
    print(f"Jobs eligible for ranking: {len(eligible)}")
    
    # --- JOB PERSISTENCE (existing jobs table via JobRepository) ---
    decision_engine = DecisionEngine()
    job_repo = JobRepository()
    saved_count = 0
    for item in eligible:
        job = item['job']
        try:
            job_repo.save({
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "url": job.url,
                "page_text": job.page_text,
                "filter_score": item['score'],
            })
            saved_count += 1
        except Exception as e:
            # Persistence failure must not break the pipeline.
            print(f"⚠️ Job persist failed ({job.title[:40]}): {e}")
    print(f"✓ Persisted {saved_count} eligible jobs to jobs table")

    # --- n8n: job match + high-priority events (fail-safe, optional) ---
    for item in eligible[:5]:
        job = item['job']
        decision = decision_engine.evaluate({"overall_score": item['score']})
        n8n_events.job_match_found(job, item['score'], decision['decision'])
        if decision['should_apply']:
            n8n_events.high_priority_job_found(job, item['score'])
    
    print("\n--- TOP 20 ---")
    for item in ranked[:20]:
        d = item['details']
        decision = decision_engine.evaluate({"overall_score": item['score']})
        print(f"Score: {item['score']} | {d['matched_role']} | {decision['decision']} | Title: {d['title']}")
        
    print("\n--- BOTTOM 10 ---")
    for item in ranked[-10:]:
        d = item['details']
        print(f"Score: {item['score']} | {d['matched_role']} | Title: {d['title']}")
    
    # --- APPLICATION PREPARATION INTEGRATION ---
    if eligible:
        try:
            top_job = eligible[0]
            print(f"\nProcessing top job: {top_job['details']['title']} at {top_job['details']['company']}")
            
            resume_plan = None
            try:
                # Pass the full details dict (contains matched_skills, missing_skills, etc.)
                resume_plan = ResumeTailor().tailor(profile, top_job['details'])
                print("✓ Resume plan generated successfully")
            except Exception as e:
                print(f"⚠️ Resume generation error: {e}")
                resume_plan = {}
                
            cover_letter = None
            try:
                # Pass profile, job object (dict), and resume_plan
                cover_letter_engine = CoverLetterEngine()
                # Build compatible dict from ranked result (CoverLetterEngine expects .get() interface)
                cover_letter_job = {
                    "company": top_job['details']['company'],
                    "title": top_job['details']['title'],
                    "url": top_job.get('url', '') or (top_job['job'].url if hasattr(top_job.get('job'), 'url') else ''),
                }
                cover_letter = cover_letter_engine.build(profile, cover_letter_job, resume_plan)
                print("✓ Cover letter generated successfully")
            except Exception as e:
                print(f"⚠️ Cover letter generation error: {e}")
                
            # Save to application repository (optional but recommended)
            try:
                app_repo = ApplicationRepository()
                # Extract url - could be in job object or details
                job_url = top_job.get('url', '')
                if not job_url and hasattr(top_job['job'], 'url'):
                    job_url = top_job['job'].url
                elif not job_url and 'details' in top_job and top_job['details'].get('url'):
                    job_url = top_job['details']['url']
                
                app_repo.save(
                    company=top_job['details']['company'],
                    title=top_job['details']['title'],
                    url=job_url,
                    applied_date=datetime.now().isoformat(),
                    status="prepared"
                )
                print("✓ Application record saved as 'prepared'")
                n8n_events.application_prepared(
                    top_job['details']['company'],
                    top_job['details']['title'],
                    job_url,
                )

                # Persist documents to disk using existing writers
                try:
                    # ResumeWriter expects: candidate, headline, location, summary,
                    # skills, experience, education, certifications, company, job_title
                    resume_doc = {
                        "candidate": profile.get("name", ""),
                        "headline": resume_plan.get("headline", "") if resume_plan else "",
                        "location": profile.get("location", ""),
                        "summary": resume_plan.get("summary", "") if resume_plan else "",
                        "skills": resume_plan.get("skills", []) if resume_plan else [],
                        "experience": resume_plan.get("experience", []) if resume_plan else [],
                        "education": resume_plan.get("education", []) if resume_plan else [],
                        "certifications": resume_plan.get("certifications", []) if resume_plan else [],
                        "company": top_job['details']['company'],
                        "job_title": top_job['details']['title'],
                    }
                    resume_path = ResumeWriter().create(resume_doc)
                    print(f"✓ Resume saved: {resume_path}")
                except Exception as e:
                    print(f"⚠️ Resume document write failed: {e}")

                try:
                    if cover_letter and cover_letter.get("cover_letter"):
                        letter_path = CoverLetterWriter().create(cover_letter["cover_letter"])
                        print(f"✓ Cover letter saved: {letter_path}")
                except Exception as e:
                    print(f"⚠️ Cover letter document write failed: {e}")
            except Exception as e:
                print(f"⚠️ Application save failed: {e}")
                
        except Exception as e:
            print(f"⚠️ Post-ranking integration failed: {e}")
    else:
        print("\nNo eligible jobs to process (all jobs rejected by alignment gate)")
    
    # --- APPLICATION LIFECYCLE (Phase 10) ---
    try:
        ai = ApplicationIntelligence()
        # The app is already prepared; now record the full pipeline state
        # (interview stages, follow-up, outcome tracking are available after apply)
        print("\nApplication Intelligence (full lifecycle tracked):")
        funnel = ai.funnel()
        print(f"  Funnel: total={funnel['total']} applied={funnel['applied']} "
              f"interviews={funnel['interviews']} offers={funnel['offers']} "
              f"rejected={funnel['rejected']} converted={funnel['applied_to_interview_pct']}%")
        followups = ai.due_followups()
        if followups:
            print(f"  Follow-ups due: {len(followups)} (check applied applications >7 days)")
        # Opportunity intelligence distinction
        if eligible:
            oi = OpportunityIntelligence(profile)
            top = eligible[0]
            score = oi.score_opportunity({"title": top['details']['title'],
                                          "company": top['details']['company'],
                                          "page_text": top['job'].page_text if hasattr(top['job'], 'page_text') else \
                                              top.get('details', {}).get('page_text', '')})
            print(f"  Top opportunity strategic value: trajectory={score['career_trajectory']}% "
                  f"good_fit={score['good_fit']} good_opportunity={score['good_opportunity']}")
    except Exception as e:
        print(f"⚠️ Application intelligence tracking skipped: {e}")

    print("\nPipeline completed successfully")

if __name__ == "__main__":
    run()