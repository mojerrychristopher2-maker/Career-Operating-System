from modules.ai.ai_service import AIService


class SummaryGenerator:

    def __init__(self):

        self.ai = AIService()

    def generate(self, profile, job):

        prompt = f"""
You are an expert resume writer.

Candidate:

{profile}

Target Job:

{job}

Write ONE ATS-friendly professional summary.

Requirements:

- 4 to 6 lines
- Professional
- No buzzwords
- Mention the candidate's strongest skills
- Mention the target role naturally
- Optimize for ATS
- Do not invent experience
"""

        return self.ai.generate(prompt)