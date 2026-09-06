"""
Career Intelligence Engine - evaluates user against all possible career paths
Builds toward: Person → Skills → Roles → Industries → Jobs → Projects → Learning → Outcomes
"""
from typing import Dict, List, Any
from collections import defaultdict, Counter
from knowledge.career_families import CAREER_FAMILIES
from knowledge.skill_weights import SKILL_WEIGHTS
from knowledge.skill_graph import SkillGraph
from modules.intelligence_v2.base_result import AnalyzerResult
from modules.intelligence.skill_gap_analyzer import SkillGapAnalyzer


class CareerIntelligenceEngine:
    """
    Evaluates user profile against ALL career paths, not just current targets.
    Identifies adjacent careers, skill gaps, and recommends learning/projects.
    """

    def __init__(self, profile: Dict[str, Any]):
        self.profile = profile
        self.user_skills = {skill.lower() for skill in profile.get("skills", [])}
        self.user_experience = profile.get("experience", [])
        self.user_projects = profile.get("projects", [])
        self.skill_graph = SkillGraph()
        self.skill_gap_analyzer = SkillGapAnalyzer()

    def analyze(self) -> Dict[str, Any]:
        """Main analysis: evaluate all career families and generate recommendations."""

        # 1. Evaluate all career families
        family_scores = self._evaluate_career_families()

        # 2. Get detailed role-level scores for top families
        role_analysis = self._analyze_top_roles(family_scores)

        # 3. Identify career gaps and adjacent opportunities
        gap_analysis = self._identify_career_gaps(role_analysis)

        # 4. Generate learning and project recommendations
        recommendations = self._generate_recommendations(gap_analysis)

        # 5. Build skill graph visualization data
        skill_graph_data = self._build_skill_graph_data()

        # 6. Calculate career trajectory and momentum
        trajectory = self._calculate_trajectory()

        return {
            "career_families": family_scores,
            "role_analysis": role_analysis,
            "gap_analysis": gap_analysis,
            "recommendations": recommendations,
            "skill_graph": skill_graph_data,
            "trajectory": trajectory,
            "metadata": {
                "analyzed_at": self._get_timestamp(),
                "user_skill_count": len(self.user_skills),
                "total_families_evaluated": len(CAREER_FAMILIES),
            }
        }

    def _evaluate_career_families(self) -> Dict[str, Dict]:
        """Score user against each career family based on skill overlap."""

        family_scores = {}

        for family_name, family_data in CAREER_FAMILIES.items():

            family_skills = set()
            for skill_list in [family_data.get("primary", []), family_data.get("secondary", [])]:
                for skill in skill_list:
                    family_skills.add(skill.lower())

            for weight_category, skills in SKILL_WEIGHTS.items():
                if any(family_name.lower() in skill.lower() or skill.lower() in family_name.lower()
                       for skill in skills):
                    family_skills.update(skill.lower() for skill in skills)

            matched_skills = self.user_skills.intersection(family_skills)
            missing_skills = family_skills.difference(self.user_skills)
            skill_match_pct = (len(matched_skills) / len(family_skills) * 100) if family_skills else 0

            experience_relevance = self._calculate_experience_relevance(family_name, family_data)
            project_alignment = self._calculate_project_alignment(family_name, family_data)

            family_weight = family_data.get("weight", 50) / 100.0
            composite_score = (
                (skill_match_pct * 0.5) +
                (experience_relevance * 0.3) +
                (project_alignment * 0.2)
            ) * family_weight

            family_scores[family_name] = {
                "score": round(composite_score, 1),
                "skill_match_pct": round(skill_match_pct, 1),
                "matched_skills": list(matched_skills),
                "missing_skills": list(missing_skills),
                "experience_relevance": round(experience_relevance, 1),
                "project_alignment": round(project_alignment, 1),
                "family_weight": family_data.get("weight", 50),
                "primary_roles": family_data.get("primary", []),
                "secondary_roles": family_data.get("secondary", []),
            }

        return dict(sorted(family_scores.items(), key=lambda x: x[1]["score"], reverse=True))

    def _calculate_experience_relevance(self, family_name: str, family_data: Dict) -> float:
        """Calculate how relevant user's experience is to this family."""

        experience_text = " ".join(self.user_experience).lower()
        family_indicators = family_data.get("primary", []) + family_data.get("secondary", [])

        matches = 0
        total_indicators = len(family_indicators)
        if total_indicators == 0:
            return 50.0

        for indicator in family_indicators:
            if indicator.lower() in experience_text:
                matches += 1

        return (matches / total_indicators) * 100 if total_indicators > 0 else 50.0

    def _calculate_project_alignment(self, family_name: str, family_data: Dict) -> float:
        """Calculate how well user's projects align with this family."""

        project_text = " ".join([
            " ".join(p.get("keywords", [])) +
            " " + p.get("description", "") +
            " " + " ".join(p.get("tools", []))
            for p in self.user_projects
        ]).lower()

        family_indicators = family_data.get("primary", []) + family_data.get("secondary", [])

        matches = 0
        total_indicators = len(family_indicators)
        if total_indicators == 0:
            return 50.0

        for indicator in family_indicators:
            if indicator.lower() in project_text:
                matches += 1

        return (matches / total_indicators) * 100 if total_indicators > 0 else 50.0

    def _analyze_top_roles(self, family_scores: Dict[str, Dict]) -> Dict[str, Any]:
        """Analyze specific roles within top-scoring families."""

        top_families = list(family_scores.keys())[:3]

        role_analysis = {
            "top_families": [],
            "role_recommendations": [],
            "adjacent_opportunities": []
        }

        for family_name in top_families:
            family_data = family_scores[family_name]
            role_analysis["top_families"].append({
                "family": family_name,
                "score": family_data["score"],
                "matched_skills": family_data["matched_skills"][:5],
                "missing_skills": family_data["missing_skills"][:5],
                "primary_roles": family_data["primary_roles"][:3],
                "secondary_roles": family_data["secondary_roles"][:3]
            })

            for role in family_data["primary_roles"][:5]:
                role_score = self._score_specific_role(role, family_name)
                role_analysis["role_recommendations"].append({
                    "role": role,
                    "family": family_name,
                    "score": role_score["score"],
                    "matched_skills": role_score["matched_skills"],
                    "missing_skills": role_score["missing_skills"],
                    "gap_priority": role_score["gap_priority"]
                })

        role_analysis["role_recommendations"] = sorted(
            role_analysis["role_recommendations"],
            key=lambda x: x["score"],
            reverse=True
        )[:10]

        return role_analysis

    def _score_specific_role(self, role: str, family: str) -> Dict[str, Any]:
        """Score user against a specific role."""

        from modules.intelligence.role_matcher import RoleMatcher

        matcher = RoleMatcher()
        role_result = matcher.score(role)

        required_skills = set()
        for fam_name, fam_data in CAREER_FAMILIES.items():
            if role in fam_data.get("primary", []) or role in fam_data.get("secondary", []):
                for skill_list in [fam_data.get("primary", []), fam_data.get("secondary", [])]:
                    required_skills.update(skill.lower() for skill in skill_list)

        for weight_category, skills in SKILL_WEIGHTS.items():
            required_skills.update(skill.lower() for skill in skills)

        matched = self.user_skills.intersection(required_skills)
        missing = required_skills.difference(self.user_skills)
        score = round((len(matched) / len(required_skills) * 100) if required_skills else 0, 1)

        if len(missing) == 0:
            gap_priority = "NONE"
        elif len(missing) <= 2:
            gap_priority = "LOW"
        elif len(missing) <= 5:
            gap_priority = "MEDIUM"
        else:
            gap_priority = "HIGH"

        return {
            "score": score,
            "matched_skills": list(matched),
            "missing_skills": list(missing),
            "gap_priority": gap_priority,
            "role_match": role_result["role"],
            "family_match": role_result["family"]
        }

    def _identify_career_gaps(self, role_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Identify skill gaps blocking career progression."""

        all_missing_skills = []
        for rec in role_analysis.get("role_recommendations", []):
            all_missing_skills.extend(rec.get("missing_skills", []))

        skill_counter = Counter(all_missing_skills)

        prioritized_gaps = []
        for skill, count in skill_counter.most_common(20):
            strategic_value = count
            is_true_gap = (count >= 2 and not any(
                rs in self.user_skills for rs in self.skill_graph.related_skills(skill)
            )) or count >= 3

            if is_true_gap:
                priority = "HIGH" if strategic_value >= 3 else "MEDIUM" if strategic_value >= 2 else "LOW"
                prioritized_gaps.append({
                    "skill": skill,
                    "frequency": count,
                    "strategic_value": strategic_value,
                    "priority": priority,
                    "related_skills": list(self.skill_graph.related_skills(skill)),
                    "learning_resources": self._get_learning_resources(skill)
                })

        return {
            "skill_gaps": prioritized_gaps,
            "total_gaps_identified": len(prioritized_gaps),
            "critical_gaps": [g for g in prioritized_gaps if g["priority"] == "HIGH"],
            "market_validation": True
        }

    def _get_learning_resources(self, skill: str) -> List[Dict[str, str]]:
        """Get recommended learning resources for a skill."""

        resource_map = {
            "aws": [
                {"type": "course", "name": "AWS Cloud Practitioner Essentials", "provider": "AWS Training", "hours": 6},
                {"type": "project", "name": "Build a serverless analytics pipeline", "description": "Use S3, Lambda, API Gateway"}
            ],
            "azure": [
                {"type": "course", "name": "Azure Fundamentals (AZ-900)", "provider": "Microsoft Learn", "hours": 8}
            ],
            "docker": [
                {"type": "course", "name": "Docker Essentials", "provider": "Docker", "hours": 4},
                {"type": "project", "name": "Containerize a Python analytics app", "description": "Package your ETL pipeline"}
            ],
            "kubernetes": [
                {"type": "course", "name": "Kubernetes Basics", "provider": "CNCF", "hours": 6}
            ],
            "spark": [
                {"type": "course", "name": "Apache Spark Fundamentals", "provider": "Databricks", "hours": 6}
            ],
            "airflow": [
                {"type": "course", "name": "Apache Airflow Fundamentals", "provider": "Astronomer", "hours": 8}
            ],
            "power bi": [
                {"type": "certification", "name": "PL-300: Power BI Data Analyst", "provider": "Microsoft", "hours": 30}
            ],
            "tableau": [
                {"type": "certification", "name": "Tableau Desktop Specialist", "provider": "Tableau", "hours": 20}
            ],
            "sql": [
                {"type": "course", "name": "SQL for Data Science", "provider": "Coursera", "hours": 25},
                {"type": "project", "name": "Build a data warehouse", "description": "Star schema with fact/dimension tables"}
            ],
            "python": [
                {"type": "course", "name": "Python for Data Analysis", "provider": "DataCamp", "hours": 30},
                {"type": "project", "name": "AI-powered analytics agent", "description": "Use LLMs for insight generation"}
            ],
            "git": [
                {"type": "course", "name": "Git and GitHub Essentials", "provider": "GitHub", "hours": 3}
            ],
            "rest apis": [
                {"type": "course", "name": "REST API Design", "provider": "Postman", "hours": 4},
                {"type": "project", "name": "Build a microservices analytics API", "description": "CRUD + authentication"}
            ],
            "machine learning": [
                {"type": "course", "name": "Machine Learning Specialization", "provider": "DeepLearning.AI", "hours": 60},
                {"type": "project", "name": "ML model deployment pipeline", "description": "End-to-end MLOps"}
            ],
            "llms": [
                {"type": "course", "name": "LLM Application Development", "provider": "DeepLearning.AI", "hours": 25},
                {"type": "project", "name": "Build a RAG application", "description": "Document QA system"}
            ]
        }

        skill_key = skill.lower().strip()
        return resource_map.get(skill_key, [
            {"type": "search", "name": f"Find {skill} tutorials", "provider": "YouTube/Google", "hours": 2}
        ])

    def _generate_recommendations(self, gap_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate concrete learning and project recommendations from gaps."""

        critical_gaps = gap_analysis.get("critical_gaps", [])
        all_gaps = gap_analysis.get("skill_gaps", [])

        learning_plan = []
        for gap in critical_gaps[:5]:
            skill = gap["skill"]
            resources = gap.get("learning_resources", [])
            learning_plan.append({
                "skill": skill,
                "priority": gap["priority"],
                "reason": f"Requested by {gap['frequency']} high-opportunity roles",
                "resources": resources[:2],
                "estimated_time": sum(r.get("hours", 0) for r in resources[:2]),
                "outcome": f"Ability to demonstrate {skill} in portfolio and interviews"
            })

        project_recommendations = self._generate_project_recommendations(critical_gaps)
        path_recommendations = self._generate_path_recommendations()

        return {
            "learning_plan": learning_plan,
            "project_recommendations": project_recommendations,
            "career_paths": path_recommendations,
            "immediate_actions": self._get_immediate_actions(learning_plan, project_recommendations)
        }

    def _generate_project_recommendations(self, critical_gaps: List[Dict]) -> List[Dict[str, Any]]:
        """Generate project ideas that address multiple skill gaps."""

        projects = []
        project_templates = [
            {"name": "Financial Analytics Dashboard", "description": "End-to-end financial reporting with automated data pipeline", "skills": ["sql", "python", "power bi", "etl", "dashboard"], "difficulty": "intermediate", "time_estimate": "3-4 weeks"},
            {"name": "Customer Churn Prediction Model", "description": "ML model to predict customer attrition with business insights", "skills": ["python", "machine learning", "sql", "statistics", "data visualization"], "difficulty": "advanced", "time_estimate": "4-6 weeks"},
            {"name": "Real-time Analytics Pipeline", "description": "Streaming analytics platform using cloud equivalents", "skills": ["python", "sql", "airflow", "docker", "kubernetes"], "difficulty": "advanced", "time_estimate": "6-8 weeks"},
            {"name": "Marketing Mix Modeling (MMM)", "description": "Statistical model to measure marketing ROI across channels", "skills": ["python", "statistics", "machine learning", "power bi", "excel"], "difficulty": "intermediate", "time_estimate": "3-5 weeks"},
            {"name": "Supply Chain Optimization Dashboard", "description": "Inventory forecasting and logistics optimization", "skills": ["sql", "python", "tableau", "power bi", "data modeling", "etl"], "difficulty": "intermediate", "time_estimate": "3-4 weeks"},
            {"name": "HR Analytics & People Insights", "description": "Employee performance, attrition, and hiring analytics", "skills": ["sql", "python", "power bi", "excel", "statistics"], "difficulty": "intermediate", "time_estimate": "3-4 weeks"}
        ]

        for template in project_templates:
            template_skills = set(s.lower() for s in template["skills"])
            gap_skills = set(g["skill"].lower() for g in critical_gaps)
            overlap = template_skills.intersection(gap_skills)
            gap_coverage = len(overlap) / len(gap_skills) if gap_skills else 0

            if gap_coverage >= 0.3:
                project_score = gap_coverage * 100
                projects.append({
                    "name": template["name"],
                    "description": template["description"],
                    "skills_gained": list(overlap),
                    "skills_missing": list(template_skills.difference(self.user_skills)),
                    "difficulty": template["difficulty"],
                    "time_estimate": template["time_estimate"],
                    "gap_coverage_pct": round(gap_coverage * 100, 1),
                    "priority_score": round(project_score, 1),
                    "recommended_order": 0
                })

        projects.sort(key=lambda x: x["priority_score"], reverse=True)
        for i, project in enumerate(projects):
            project["recommended_order"] = i + 1
        return projects[:5]

    def _generate_path_recommendations(self) -> List[Dict[str, Any]]:
        """Generate strategic career path recommendations."""

        paths = []
        strong_areas = []
        if any(s in self.user_skills for s in ["power bi", "tableau", "sql", "excel"]):
            strong_areas.append("business_intelligence")
        if any(s in self.user_skills for s in ["python", "pandas", "machine learning", "sql"]):
            strong_areas.append("data_science")
        if any(s in self.user_skills for s in ["aws", "azure", "docker", "kubernetes"]):
            strong_areas.append("cloud_engineering")
        if any(s in self.user_skills for s in ["git", "github", "python", "apis"]):
            strong_areas.append("software_engineering")

        path_mapping = {
            "business_intelligence": [
                {"role": "Analytics Engineer", "reason": "Strong SQL/Python foundation, add ETL/modeling skills"},
                {"role": "Data Engineer", "reason": "BI background valuable for data infrastructure roles"},
                {"role": "AI Solutions Engineer", "reason": "Bridge BI and ML - add ML/deployment skills"}
            ],
            "data_science": [
                {"role": "Machine Learning Engineer", "reason": "Add software engineering and ML ops to modeling skills"},
                {"role": "AI Engineer", "reason": "Focus on LLM application and prompt engineering"},
                {"role": "Data Scientist (Research)", "reason": "Deepen statistical modeling and experimentation"}
            ],
            "cloud_engineering": [
                {"role": "Cloud Data Engineer", "reason": "Combine cloud infra with data pipeline expertise"},
                {"role": "DevOps Engineer", "reason": "Add CI/CD and automation to cloud administration"},
                {"role": "Site Reliability Engineer (SRE)", "reason": "Focus on reliability, monitoring, incident response"}
            ],
            "software_engineering": [
                {"role": "Full Stack Developer", "reason": "Add frontend/backend frameworks to current skills"},
                {"role": "Backend Engineer", "reason": "Specialize in APIs, databases, and system design"},
                {"role": "Cloud Solutions Architect", "reason": "Design scalable cloud systems using current skills"}
            ]
        }

        for area in strong_areas:
            if area in path_mapping:
                for path_info in path_mapping[area][:2]:
                    required_skills = self._get_role_skills(path_info["role"])
                    matched = self.user_skills.intersection(required_skills)
                    fit_pct = round((len(matched) / len(required_skills) * 100) if required_skills else 0, 1)

                    paths.append({
                        "role": path_info["role"],
                        "current_fit_pct": fit_pct,
                        "reason": path_info["reason"],
                        "skill_gaps": list(required_skills.difference(self.user_skills)),
                        "strategic_value": "HIGH" if fit_pct >= 60 else "MEDIUM" if fit_pct >= 40 else "LOW",
                        "recommended_learning": self._get_learning_resources(
                            list(required_skills.difference(self.user_skills))[0]
                        ) if required_skills.difference(self.user_skills) else []
                    })

        paths.sort(key=lambda x: (x["strategic_value"] == "HIGH", x["current_fit_pct"]), reverse=True)
        return paths[:8]

    def _get_role_skills(self, role: str) -> set:
        """Get typical skills required for a role."""
        role_skills_map = {
            "analytics engineer": {"sql", "python", "etl", "data modeling", "airflow", "dbt", "git"},
            "data engineer": {"sql", "python", "etl", "aws", "azure", "spark", "kafka", "docker"},
            "ai solutions engineer": {"python", "machine learning", "llms", "prompt engineering", "apis", "docker", "cloud"},
            "machine learning engineer": {"python", "machine learning", "deep learning", "mlops", "docker", "kubernetes", "git"},
            "ai engineer": {"python", "llms", "prompt engineering", "rag", "fine-tuning", "apis", "cloud"},
            "cloud data engineer": {"sql", "python", "etl", "aws", "azure", "gcp", "spark", "databricks", "airflow"},
            "devops engineer": {"docker", "kubernetes", "ci/cd", "jenkins", "git", "bash", "monitoring", "iac"},
            "site reliability engineer": {"monitoring", "logging", "incident response", "python", "golang", "kubernetes", "aws"},
            "full stack developer": {"javascript", "react", "node.js", "python", "sql", "git", "rest apis", "html/css"},
            "backend engineer": {"python", "java", "sql", "apis", "microservices", "docker", "git", "rest apis"},
            "cloud solutions architect": {"aws", "azure", "gcp", "architecture", "networking", "security", "cost optimization"}
        }
        return role_skills_map.get(role.lower(), set())

    def _get_immediate_actions(self, learning_plan: List[Dict], project_recommendations: List[Dict]) -> List[Dict[str, str]]:
        """Get immediate next actions."""
        actions = []

        if learning_plan:
            top_learning = learning_plan[0]
            actions.append({
                "action": f"Start learning {top_learning['skill']}",
                "details": f"Begin with: {top_learning['resources'][0]['name'] if top_learning['resources'] else 'introductory course'}",
                "timeframe": "1-2 weeks",
                "priority": "HIGH"
            })

        if project_recommendations:
            top_project = project_recommendations[0]
            actions.append({
                "action": f"Scope project: {top_project['name']}",
                "details": f"Define MVP and gather required resources for: {top_project['description']}",
                "timeframe": "3-5 days",
                "priority": "HIGH"
            })

        actions.append({
            "action": "Update skill inventory",
            "details": "Add newly learned skills to profile as you complete them",
            "timeframe": "Ongoing",
            "priority": "MEDIUM"
        })

        return actions[:3]

    def _build_skill_graph_data(self) -> Dict[str, Any]:
        """Build data structure for skill graph visualization."""
        nodes = []
        edges = []

        for skill in sorted(self.user_skills):
            nodes.append({
                "id": skill,
                "label": skill.title(),
                "type": "user_skill",
                "level": self._get_skill_level(skill)
            })

        adjacent_skills = {"aws", "docker", "kubernetes", "machine learning", "llms", "apis", "etl", "dbt"}
        for skill in adjacent_skills:
            if skill not in self.user_skills:
                nodes.append({
                    "id": skill,
                    "label": skill.title(),
                    "type": "target_skill",
                    "level": "to_learn"
                })

        for skill in self.user_skills:
            related = self.skill_graph.related_skills(skill)
            for rel_skill in related:
                if rel_skill in self.user_skills or rel_skill in adjacent_skills:
                    edges.append({"source": skill, "target": rel_skill, "type": "related"})

        return {"nodes": nodes, "edges": edges, "skill_families": self._get_skill_families()}

    def _get_skill_level(self, skill: str) -> str:
        return "intermediate"

    def _get_skill_families(self) -> Dict[str, List[str]]:
        families = defaultdict(list)
        for skill in self.user_skills:
            for family_name, family_data in CAREER_FAMILIES.items():
                all_skills = family_data.get("primary", []) + family_data.get("secondary", [])
                if any(skill in s.lower() or s.lower() in skill for s in all_skills):
                    families[family_name].append(skill)
                    break
            else:
                families["other"].append(skill)
        return dict(families)

    def _calculate_trajectory(self) -> Dict[str, Any]:
        return {
            "momentum": "building",
            "skill_growth_rate": "moderate",
            "market_alignment": "good",
            "next_milestone": "Complete AWS fundamentals and build cloud analytics project",
            "estimated_time_to_next_level": "8-12 weeks"
        }

    def _get_timestamp(self) -> str:
        from datetime import datetime
        return datetime.now().isoformat()


# Convenience function
def analyze_career_intelligence(profile: Dict[str, Any]) -> Dict[str, Any]:
    engine = CareerIntelligenceEngine(profile)
    return engine.analyze()