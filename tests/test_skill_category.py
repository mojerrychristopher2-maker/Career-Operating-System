from modules.intelligence.candidate_scorer import CandidateScorer

scorer = CandidateScorer()

print("=" * 60)

print("SKILL CATEGORY TEST")

print("=" * 60)

for skill in [

    "SQL",

    "Excel",

    "Azure",

    "Docker"

]:

    print(

        skill,

        "->",

        scorer.get_skill_category(skill)

    )