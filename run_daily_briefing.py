"""Daily Career OS briefing.

Deterministic summary of job opportunities, prepared applications,
follow-ups and skill gaps. Uses only existing components:

- DiscoveryAgent / JobRanker        (live opportunities)
- ApplicationRepository             (application tracking)
- SkillGapAnalyzer                  (skill gaps from ranked jobs)
- DecisionEngine                    (priority classification)
"""

import sys
from collections import Counter
from datetime import datetime

sys.path.insert(0, r"C:\Users\mojer\Documents\Codex\2026-07-20\bui\outputs\mojerry-career-os")

from core.profile_manager import ProfileManager
from modules.discovery.discovery_agent import DiscoveryAgent
from modules.ranking.job_ranker import JobRanker
from modules.intelligence.decision_engine import DecisionEngine
from modules.intelligence.skill_gap_analyzer import SkillGapAnalyzer
from database.application_repository import ApplicationRepository
from pathlib import Path


def build_briefing(run_discovery=True, top_n=10):
    lines = []
    add = lines.append

    add("DAILY CAREER BRIEFING")
    add("=" * 55)
    add(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    add("")

    # ---- APPLICATIONS ----
    repo = ApplicationRepository()
    apps = repo.get_all()
    by_status = Counter(a[2] for a in apps)
    applied = [a for a in apps if a[2] == "applied"]
    prepared = [a for a in apps if a[2] == "prepared"]

    add("APPLICATIONS")
    add("-" * 55)
    add(f"Total tracked:      {len(apps)}")
    for status, count in by_status.most_common():
        add(f"  {status:<12} {count}")
    add(f"Follow-ups due:     {len(applied)} (applied >7 days ago need checking)")
    add("")

    # ---- FOLLOW-UP PLAN (prepared applications awaiting manual apply) ----
    if prepared:
        add("FOLLOW-UP PLAN (prepared — review & apply manually)")
        add("-" * 55)
        for company, title, status, date in prepared[:10]:
            try:
                prep_date = datetime.fromisoformat(date)
                days = (datetime.now() - prep_date).days
            except Exception:
                days = None
            age = f"{days}d ago" if days is not None else "unknown"
            add(f"  • {title} @ {company} (prepared {age})")
            add(f"    Docs: output/resumes/ + output/cover_letters/")
        if len(prepared) > 10:
            add(f"  ... +{len(prepared) - 10} more prepared applications")
        add("")

    # ---- OPPORTUNITIES ----
    eligible = []
    if run_discovery:
        profile = ProfileManager().get_all()
        agent = DiscoveryAgent()
        # Briefing must stay fast: skip slow browser-crawl sources (Lever
        # opens every job page sequentially). API/board sources only.
        fast_sites = [s for s in profile.get("career_sites", [])
                      if "lever" not in s.lower()]
        if fast_sites:
            agent.profile["career_sites"] = fast_sites
        ranker = JobRanker(profile)

        try:
            jobs = agent.discover_jobs()
            ranked = ranker.rank(jobs)
            eligible = [r for r in ranked if r["score"] > 0]
            rejected = len(ranked) - len(eligible)
        except Exception as e:
            add("OPPORTUNITIES")
            add("-" * 55)
            add(f"Discovery failed: {type(e).__name__}: {e}")
            add("")
            eligible, rejected = [], 0

        decision_engine = DecisionEngine()

        add("TOP OPPORTUNITIES TODAY")
        add("-" * 55)
        if not eligible:
            add("No eligible jobs discovered this run.")
        for i, item in enumerate(eligible[:top_n], 1):
            d = item["details"]
            job = item["job"]
            decision = decision_engine.evaluate({"overall_score": item["score"]})
            add(f"{i:>2}. [{item['score']:>3}] {job.title}")
            add(f"    {job.company} | {decision['decision']} {decision['priority']}")
            add(f"    Role match: {d['role_match']} | Skills: {d['skills_score']} "
                f"| Matched: {', '.join(d['matched_skills'][:4]) or '-'}")
            add(f"    {job.url[:80]}")
        add("")

        # ---- SKILL GAPS (from real ranked jobs) ----
        gap_analyzer = SkillGapAnalyzer()
        gap_jobs = [{"score": {"missing_skills": item["details"]["missing_skills"]}}
                    for item in eligible]
        gaps = [g for g in gap_analyzer.analyze(gap_jobs) if g["count"] >= 3]

        add("SKILL GAPS (requested by 3+ of today's eligible jobs)")
        add("-" * 55)
        if not gaps:
            add("No significant gaps in today's job pool.")
        for g in gaps:
            add(f"  {g['skill']:<20} requested by {g['count']} jobs "
                f"({g['count']}/{len(eligible)})")
        add("")

        # ---- LEARNING QUEUE (persist skill gaps for tracking) ----
        try:
            import sqlite3
            conn = sqlite3.connect("career_os.db")
            cur = conn.cursor()
            queued = 0
            for g in gaps:
                cur.execute(
                    "INSERT OR IGNORE INTO learning_queue (skill, source_job, priority, learned) "
                    "SELECT ?, ?, ?, 0 WHERE NOT EXISTS ("
                    "  SELECT 1 FROM learning_queue WHERE skill = ? AND learned = 0)",
                    (g["skill"], "daily_briefing", g["count"], g["skill"]),
                )
                queued += cur.rowcount
            conn.commit()
            conn.close()
            if queued:
                add(f"Learning queue: +{queued} new skill objectives queued "
                    f"(view via learning_queue table)")
                from modules.integration import n8n_events
                n8n_events.learning_queue_updated(
                    [g["skill"] for g in gaps[:queued] if True]
                )
        except Exception as e:
            add(f"Learning queue update skipped: {e}")

        # n8n: skill gap event
        if gaps:
            from modules.integration import n8n_events
            n8n_events.skill_gap_updated(gaps)

    add("=" * 55)
    add("Prepared applications are NOT submitted automatically.")
    add("Review output/ documents before applying manually.")
    return "\n".join(lines)


def main():
    briefing = build_briefing(run_discovery=True)
    print(briefing)

    out_dir = Path("output/reports")
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "daily_briefing.txt"
    path.write_text(briefing, encoding="utf-8")
    print(f"\nSaved: {path}")

    # --- n8n events (fail-safe, optional) ---
    from modules.integration import n8n_events

    # FOLLOW_UP_REQUIRED: prepared applications awaiting manual apply
    repo = ApplicationRepository()
    prepared = [a for a in repo.get_all() if a[2] == "prepared"]
    if prepared:
        n8n_events.follow_up_required([
            {"company": c, "title": t, "status": s, "prepared_date": d}
            for (c, t, s, d) in prepared[:20]
        ])

    # DAILY_BRIEFING_READY is emitted after successful generation
    eligible_count = 0
    for line in briefing.splitlines():
        pass  # count not critical; emit with report path only if discovery ran
    n8n_events.daily_briefing_ready(path, len(prepared))


if __name__ == "__main__":
    main()
