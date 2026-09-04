TARGET_CAREERS = {
    # Tier 1 — primary targets
    "business intelligence analyst": 100,
    "bi analyst": 100,
    "data analyst": 100,

    # Tier 2 — strong targets
    "reporting analyst": 95,
    "analytics analyst": 95,
    "business analyst": 90,
    "power bi developer": 90,
    "bi developer": 90,
    "business intelligence developer": 90,
    "sql developer": 90,

    # Tier 3 — related targets
    "data reporting analyst": 90,
    "data quality analyst": 85,
    "data operations analyst": 85,
    "kpi analyst": 85,
    "insights analyst": 85,
    "data visualization analyst": 85,
    "data visualization specialist": 80,
    "operations analyst": 80,
    "analytics consultant": 85,
    "dashboard developer": 85,
    "data operations": 75,

    # Tier 4 — adjacent titles commonly used by employers (verified gap:
    # real boards list these variants; they align with profile skills)
    "analytics engineer": 85,
    "bi engineer": 85,
    "business intelligence engineer": 85,
    "analytics specialist": 80,
    "data specialist": 80,
    "reporting specialist": 80,
    "bi support analyst": 80,
    "product data analyst": 90,

    # Broad phrases are useful to discovery and description analysis, but not
    # sufficient for direct role matching.
    "business intelligence": 75,
    "power bi": 70,
    "data visualization": 65,
}

# RoleMatcher rejects these leadership titles for the current early-career
# strategy.  Senior individual-contributor roles remain reviewable and are
# handled by CandidateScorer's separate seniority dimension.
LEADERSHIP_TERMS = {
    "manager",
    "director",
    "head",
    "vp",
    "principal",
    "staff",
    "lead",
}

EXCLUDED_CAREERS = {
    "research engineer": 0,
    "machine learning": 0,
    "ml engineer": 0,
    "infrastructure": 0,
    "cyber": 0,
    "security": 0,
    "devops": 0,
    "software engineer": 0,
    "backend": 0,
    "frontend": 0,
    "full stack": 0,
    "performance engineer": 0,
    "rl": 0,
    "reinforcement learning": 0,
    "life sciences": 0,
    "chip design": 0,
}
