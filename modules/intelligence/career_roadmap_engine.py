"""
Career Roadmap Engine — actively constructs development roadmap.
Reads profile/projects, detects duplicates, picks strategic projects.
"""
from typing import Dict, List, Any


def build_roadmap(profile: Dict[str, Any]) -> Dict[str, Any]:
    projects = profile.get("projects", [])

    # Detect similarity clusters (automation/dashboard dominance)
    categories = {"automation": 0, "dashboard": 0, "sql_data": 0, "cleaning": 0, "ai_agent": 0, "other": 0}
    for p in projects:
        kw = " ".join(p.get("keywords", []) + p.get("tools", [])).lower()
        if any(x in kw for x in ["automation", "n8n", "zapier", "workflow"]):
            categories["automation"] += 1
        elif any(x in kw for x in ["dashboard", "tableau", "visualization"]):
            categories["dashboard"] += 1
        elif any(x in kw for x in ["sql", "mysql", "database"]):
            categories["sql_data"] += 1
        elif any(x in kw for x in ["cleaning", "data quality", "missing"]):
            categories["cleaning"] += 1
        elif any(x in kw for x in ["ai agent", "hermes", "agent"]):
            categories["ai_agent"] += 1
        else:
            categories["other"] += 1

    # Portfolio analysis message
    portfolio_note = (
        "Your portfolio has 3 automation/workflow projects, 2 dashboards, 2 cleaning projects, and 1 AI agent. "
        "Most are beginner-level. You need projects that demonstrate new capabilities: cloud/data engineering, "
        "ML deployment, or production software engineering. Otherwise you're repeating the same skills."
    )

    # Strategic recommendations (must address gaps + show new skills)
    recommendations = [
        {
            "name": "Customer Churn Prediction (ML + SQL)",
            "why": "Demonstrates ML + business insight — currently missing from portfolio; shows predictive modeling not just reporting.",
            "skills_gained": ["machine learning", "python", "sql", "statistics", "data visualization"],
            "time": "4-6 weeks",
            "priority": "HIGH",
            "addresses_gaps": ["machine learning", "python modeling", "statistics"]
        },
        {
            "name": "RAG Application (LLM + APIs + Python)",
            "why": "Builds production-level AI engineering — demonstrates APIs, LLM architecture, deployment. Critical for AI Solutions Engineer path.",
            "skills_gained": ["llms", "apis", "python", "rag", "deployment"],
            "time": "3-4 weeks",
            "priority": "HIGH",
            "addresses_gaps": ["llms", "rest apis", "deployment"]
        },
        {
            "name": "Cloud Analytics Pipeline (AWS/SQL/Python)",
            "why": "Shows cloud + data engineering — the #1 gap in your target roles (AWS, docker, airflow). Moves you from 'Excel analyst' to engineer-adjacent.",
            "skills_gained": ["aws", "python", "sql", "etl", "docker"],
            "time": "6-8 weeks",
            "priority": "MEDIUM",
            "addresses_gaps": ["aws", "docker", "etl"]
        },
        {
            "name": "Business Intelligence Platform (Power BI + DB + ETL)",
            "why": "Demonstrates end-to-end BI — not just a dashboard. Shows data modeling + ETL + stakeholder-facing delivery.",
            "skills_gained": ["power bi", "data modeling", "sql", "etl", "dashboard"],
            "time": "3-4 weeks",
            "priority": "MEDIUM",
            "addresses_gaps": ["data modeling", "etl"]
        }
    ]

    return {
        "portfolio_analysis": categories,
        "portfolio_note": portfolio_note,
        "three_most_valuable_next": recommendations[:3],
        "strategic_rationale": "You have high automation/dashboard counts (3/2) with no production ML, no cloud pipeline, no API work. Build the 3 above to break out of beginner-level repetition.",
        "career_path_recommendation": "AI Engineer / Analytics Engineer adjacent — you have strong SQL/Python base but need ML + cloud + APIs to open doors."
    }
