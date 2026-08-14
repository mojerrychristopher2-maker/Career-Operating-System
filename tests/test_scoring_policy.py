import pytest

from knowledge.career_strategy import TARGET_CAREERS
from knowledge.role_weights import ROLE_WEIGHTS
from modules.discovery.job import Job, normalize_url
from modules.intelligence.candidate_scorer import CandidateScorer
from modules.intelligence.role_matcher import RoleMatcher


PROFILE = {
    "skills": ["SQL", "Python", "Power BI", "Excel", "Tableau", "Git"],
    "education": ["Bachelor of Arts (Humanities), University of Johannesburg"],
    "certifications": ["Alex The Analyst Data Analyst Bootcamp"],
}


def make_job(title, skills=None, description=""):
    return Job(
        title=title,
        company="Test Company",
        location="Remote",
        url="https://example.test/jobs/1",
        description=description,
        source="test",
        skills=skills or ["SQL", "Power BI", "Excel"],
        page_text=description,
    )


@pytest.mark.parametrize(
    "title",
    [
        "Data Analyst",
        "Junior Data Analyst",
        "Graduate Data Analyst",
        "Senior Data Analyst",
        "BI Analyst",
        "BI Developer",
        "Power BI Developer",
        "Reporting Analyst",
        "Data Visualization Analyst",
        "Data Quality Analyst",
        "Data Operations Analyst",
    ],
)
def test_target_titles_are_data_family_matches(title):
    result = CandidateScorer(PROFILE).score(make_job(title))

    assert result["career_family"] == "data"
    assert result["role_match"] >= 85
    assert result["overall_score"] >= 70
    assert result["recommendation"] != "Reject - role is not aligned"


def test_score_exposes_all_explainability_dimensions_for_aligned_jobs():
    result = CandidateScorer(PROFILE).score(make_job("Data Analyst"))

    assert {
        "matched_role", "role_match", "career_family", "career_goal_score",
        "skills_score", "seniority_score", "experience_score", "education_score",
        "certification_score", "target_role_score", "matched_skills",
        "missing_skills", "recommendation", "role_reason",
    }.issubset(result)


@pytest.mark.parametrize(
    "title",
    [
        "Data Analytics Manager",
        "Analytics Manager",
        "BI Manager",
        "Senior Manager - Analytics Engineering",
        "Customer Success Manager",
        "Product Manager",
        "Software Engineer",
        "Software Development Engineer III",
        "Software Development Engineer in Test III",
        "Research Engineer",
        "Cybersecurity Analyst",
        "Benefits Operations Manager",
    ],
)
def test_unrelated_or_management_titles_are_rejected(title):
    result = CandidateScorer(PROFILE).score(make_job(title))

    assert result["overall_score"] == 0
    assert result["recommendation"] == "Reject - role is not aligned"


def test_managerial_variant_of_direct_target_is_rejected_before_skills_can_help():
    result = CandidateScorer(PROFILE).score(make_job("Data Analyst Manager"))

    assert result["role_match"] == 0
    assert result["overall_score"] == 0
    assert result["recommendation"] == "Reject - role is not aligned"


def test_generic_analytics_term_does_not_create_a_data_family_match():
    result = RoleMatcher().score("Senior Manager - Analytics Engineering")

    assert result["family"] != "data"
    assert result["score"] == 0


def test_role_weights_are_a_compatibility_view_of_the_authoritative_strategy():
    broad_phrases = {"business intelligence", "power bi", "data visualization"}
    expected = {
        role: score
        for role, score in TARGET_CAREERS.items()
        if role not in broad_phrases
    }

    assert ROLE_WEIGHTS == expected


def test_normalize_url_unwraps_hermes_markdown_url_artifacts():
    assert normalize_url(
        "[@url:`https://example.test/jobs/1`](@url:`https://example.test/jobs/1`)"
    ) == "https://example.test/jobs/1"


def test_candidate_scorer_requires_a_job_object_at_its_domain_boundary():
    with pytest.raises(TypeError, match="Job"):
        CandidateScorer(PROFILE).score({"title": "Data Analyst", "skills": []})
