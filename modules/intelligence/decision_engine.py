class DecisionEngine:

    def evaluate(self, score):

        overall = score["overall_score"]

        if overall >= 90:
            return {
                "decision": "APPLY IMMEDIATELY",
                "priority": "★★★★★",
                "status": "Perfect Match",
                "should_apply": True
            }

        elif overall >= 80:
            return {
                "decision": "APPLY",
                "priority": "★★★★",
                "status": "Strong Match",
                "should_apply": True
            }

        elif overall >= 70:
            return {
                "decision": "REVIEW MANUALLY",
                "priority": "★★★",
                "status": "Possible Match",
                "should_apply": False
            }

        elif overall >= 50:
            return {
                "decision": "LEARN MISSING SKILLS",
                "priority": "★★",
                "status": "Weak Match",
                "should_apply": False
            }

        return {
            "decision": "SKIP",
            "priority": "★",
            "status": "Poor Match",
            "should_apply": False
        }