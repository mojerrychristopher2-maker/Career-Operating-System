from collections import Counter
from modules.intelligence.skill_gap_analyzer import SkillGapAnalyzer


class DashboardEngine:

    def generate(self, jobs):

        total_jobs = len(jobs)

        perfect = strong = good = possible = skipped = 0

        company_counter = Counter()

        total_score = 0

        for job in jobs:

            score = job.get("score", {}).get("overall_score", 0)

            total_score += score

            company_counter[job.get("company", "Unknown")] += 1

            if score >= 90:
                perfect += 1

            elif score >= 75:
                strong += 1

            elif score >= 60:
                good += 1

            elif score >= 40:
                possible += 1

            else:
                skipped += 1

        average = round(total_score / total_jobs) if total_jobs else 0

        skill_gaps = SkillGapAnalyzer().analyze(jobs)

        return {

            "total_jobs": total_jobs,

            "perfect_matches": perfect,

            "strong_matches": strong,

            "good_matches": good,

            "possible_matches": possible,

            "skipped": skipped,

            "average_match": average,

            "top_companies": company_counter.most_common(10),

            "top_skill_gaps": skill_gaps[:10]

        }