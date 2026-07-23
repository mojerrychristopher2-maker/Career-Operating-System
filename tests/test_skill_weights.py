from modules.intelligence.candidate_scorer import CandidateScorer

scorer = CandidateScorer()

print("=" * 60)
print("SKILL WEIGHTS")
print("=" * 60)

print(scorer.skill_weights)