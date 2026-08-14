"""Compatibility export for legacy callers.

Career strategy lives in ``knowledge.career_strategy``.  RoleMatcher imports
this name so older modules keep working without a second mutable role-weight
source of truth.
"""

from knowledge.career_strategy import TARGET_CAREERS


BROAD_CAREER_PHRASES = {
    "business intelligence",
    "power bi",
    "data visualization",
}

# Broad phrases are discovery/search signals, not direct job-role matches.
ROLE_WEIGHTS = {
    role: weight
    for role, weight in TARGET_CAREERS.items()
    if role not in BROAD_CAREER_PHRASES
}
