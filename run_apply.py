"""Run ApplyPipeline: discover → rank → tailor resume/cover → auto-apply via Playwright.

Usage:
  python run_apply.py            # dry-run: fills form + uploads docs, no submit
  python run_apply.py --submit   # actually submits
  python run_apply.py --top 3    # apply to top 3 eligible jobs (default 3)
"""
import sys
sys.path.insert(0, r"C:\Users\mojer\Documents\Codex\2026-07-20\bui\outputs\mojerry-career-os")

import argparse
from modules.application.apply_pipeline import ApplyPipeline
from modules.integration import n8n_events


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--submit", action="store_true", help="Actually submit applications")
    parser.add_argument("--top", type=int, default=3, help="Number of top jobs to apply to")
    args = parser.parse_args()

    print(f"=== Career OS Apply Pipeline ({'LIVE' if args.submit else 'DRY-RUN'}) ===")
    pipeline = ApplyPipeline(dry_run=not args.submit)
    results = pipeline.run(top_n=args.top)

    for i, r in enumerate(results, 1):
        print(f"\n{i}. {r['company']} - {r['job_title']}")
        print(f"   Decision: {r['decision']['decision']} | Submitted: {r['submitted']}")
        print(f"   Resume: {r['resume_path']}")
        print(f"   Cover:  {r['cover_letter_path']}")

    # n8n events
    n8n_events.daily_briefing_ready(  # Reuse existing event for completion
        "output/reports/apply_run.txt",
        len(results)
    )


if __name__ == "__main__":
    main()
