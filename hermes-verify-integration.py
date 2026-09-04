import sys, os, json
sys.path.insert(0, r"C:\Users\mojer\Documents\Codex\2026-07-20\bui\outputs\mojerry-career-os")

from core.profile_manager import ProfileManager
from modules.discovery.discovery_agent import DiscoveryAgent
from modules.ranking.job_ranker import JobRanker
from modules.builder.resume_tailor import ResumeTailor
from modules.cover_letter.cover_letter_engine import CoverLetterEngine
from database.application_repository import ApplicationRepository
from datetime import datetime

print("=" * 60)
print("SELECTIVE VERIFICATION (NO LIVE DISCOVERY)")
print("=" * 60)

# Mock job data for testing
mock_ranked_job = {
    'score': 95,
    'details': {
        'title': 'Data Analyst',
        'company': 'Test Corp',
        'url': 'https://example.com/jobs/test',
        'matched_role': 'Data Analyst',
        'career_family': 'data',
        'seniority_score': 80,
        'recommendation': 'STRONG_MATCH'
    }
}

profile = ProfileManager().get_all()
print(f"Profile loaded: {profile.get('name', 'Unknown')}")

# Test 1: ResumeTailor
print("\n--- Testing ResumeTailor ---")
try:
    rl = ResumeTailor()
    resume_plan = rl.tailor(profile, mock_ranked_job['score'])
    print(f"SUCCESS: ResumeTailor.tailor() returned: {type(resume_plan).__name__}")
    if isinstance(resume_plan, dict):
        print(f"  Resume plan keys: {list(resume_plan.keys())}")
except Exception as e:
    print(f"FAIL: ResumeTailor error: {e}")

# Test 2: CoverLetterEngine
print("\n--- Testing CoverLetterEngine ---")
try:
    cl = CoverLetterEngine.build(profile, mock_ranked_job, resume_plan if 'resume_plan' in dir() else {})
    print(f"SUCCESS: CoverLetterEngine.build() returned: {type(cl).__name__}")
    print(f"  Cover letter length: {len(str(cl))} chars")
except Exception as e:
    print(f"FAIL: CoverLetterEngine error: {e}")

# Test 3: ApplicationRepository
print("\n--- Testing ApplicationRepository ---")
try:
    ar = ApplicationRepository()
    ar.save(
        company=mock_ranked_job['details']['company'],
        title=mock_ranked_job['details']['title'],
        url=mock_ranked_job['details']['url'],
        applied_date=datetime.now().isoformat(),
        status="prepared"
    )
    apps = ar.get_all()
    print(f"SUCCESS: ApplicationRepository.save() success, total apps: {len(apps)}")
except Exception as e:
    print(f"FAIL: ApplicationRepository error: {e}")

print("\n" + "=" * 60)
print("SELECTIVE VERIFICATION COMPLETE")
print("=" * 60)