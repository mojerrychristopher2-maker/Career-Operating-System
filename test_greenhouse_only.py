import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.profile_manager import ProfileManager
from modules.discovery.discovery_agent import DiscoveryAgent
from modules.ranking.job_ranker import JobRanker

def run_greenhouse_only():
    print("Initializing Discovery Agent (Greenhouse only)...")
    profile = ProfileManager().get_all()
    # Temporarily modify career_sites to only include Greenhouse
    original_sites = profile.get("career_sites", [])
    greenhouse_sites = [site for site in original_sites if "greenhouse" in site]
    profile["career_sites"] = greenhouse_sites
    
    agent = DiscoveryAgent()
    ranker = JobRanker(profile)
    
    print("Starting discovery (Greenhouse only)...")
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
    
    print("\n--- TOP 20 ---")
    for item in ranked[:20]:
        d = item['details']
        print(f"Score: {item['score']} | {d['matched_role']} | {d['role_match']} | {d['career_family']} | {d['seniority_score']} | {d['recommendation']} | Title: {d['title']}")
    
    print("\n--- BOTTOM 10 ---")
    for item in ranked[-10:]:
        d = item['details']
        print(f"Score: {item['score']} | {d['matched_role']} | Title: {d['title']}")
    
    # Restore original profile (not necessary as we are in a script, but good practice)
    profile["career_sites"] = original_sites

if __name__ == "__main__":
    run_greenhouse_only()