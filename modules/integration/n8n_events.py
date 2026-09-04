"""Optional n8n event dispatcher for Career OS.

Fail-safe by design:
- No N8N_WEBHOOK_URL configured -> events are silently skipped.
- Timeout / HTTP error / malformed URL -> logged, never raised.
- Career OS never depends on n8n being reachable.

Duplicate protection: an in-process set of recent event signatures
(event type + primary key) prevents repeat emissions in one run.
"""

import json
import os
import urllib.error
import urllib.request
from datetime import datetime

WEBHOOK_TIMEOUT = 10


def _webhook_url():
    url = os.environ.get("N8N_WEBHOOK_URL", "").strip()
    if not url.startswith(("http://", "https://")):
        return None
    return url


_recent = set()


def _duplicate(event_type, key):
    sig = (event_type, key)
    if sig in _recent:
        return True
    _recent.add(sig)
    return False


def emit_event(event_type, data=None, dedup_key=None):
    """Emit an event to the configured n8n webhook. Never raises."""
    if dedup_key and _duplicate(event_type, dedup_key):
        return False

    url = _webhook_url()
    if not url:
        return False  # n8n not configured — normal operation

    payload = {
        "event_type": event_type,
        "timestamp": datetime.now().isoformat(),
        "source": "career_os",
        "data": data or {},
    }

    try:
        request = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json",
                     "User-Agent": "CareerOS/1.0"},
        )
        with urllib.request.urlopen(request, timeout=WEBHOOK_TIMEOUT) as response:
            status = response.getcode()
        print(f"→ n8n event sent: {event_type} (HTTP {status})")
        return True
    except urllib.error.HTTPError as e:
        print(f"⚠️ n8n event {event_type}: HTTP {e.code} (continuing)")
    except Exception as e:
        print(f"⚠️ n8n event {event_type} failed: {type(e).__name__} (continuing)")
    return False


# ---- Typed convenience emitters -------------------------------------------

def job_match_found(job, score, decision):
    return emit_event("JOB_MATCH_FOUND", {
        "title": job.title, "company": job.company, "url": job.url,
        "score": score, "decision": decision,
    }, dedup_key=job.url)


def high_priority_job_found(job, score):
    return emit_event("HIGH_PRIORITY_JOB_FOUND", {
        "title": job.title, "company": job.company, "url": job.url,
        "score": score,
    }, dedup_key=f"{job.url}:{score}")


def application_prepared(company, title, url, status="prepared"):
    return emit_event("APPLICATION_PREPARED", {
        "company": company, "title": title, "url": url, "status": status,
    }, dedup_key=url)


def daily_briefing_ready(report_path, eligible_count):
    return emit_event("DAILY_BRIEFING_READY", {
        "report_path": str(report_path), "eligible_jobs": eligible_count,
    })


def skill_gap_updated(gaps):
    return emit_event("SKILL_GAP_UPDATED", {"gaps": gaps},
                      dedup_key=tuple(sorted(g["skill"] for g in gaps)))


def learning_queue_updated(new_objectives):
    return emit_event("LEARNING_QUEUE_UPDATED",
                      {"objectives": new_objectives},
                      dedup_key=tuple(sorted(new_objectives)))


def follow_up_required(applications):
    return emit_event("FOLLOW_UP_REQUIRED",
                      {"applications": applications},
                      dedup_key=tuple(sorted(a["url"] for a in applications
                                             if isinstance(a, dict) and "url" in a)))
