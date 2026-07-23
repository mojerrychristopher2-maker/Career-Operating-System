class AIService:

    def generate_summary(

        self,

        profile,

        company,

        title

    ):

        prompt = f"""
You are a professional resume writer.

Candidate:
{profile['name']}

Headline:
{profile['headline']}

Skills:
{', '.join(profile['skills'])}

Experience:
{', '.join(profile['experience'])}

Target Company:
{company}

Job Title:
{title}

Write a concise professional summary (3-5 sentences)
that is ATS-friendly, confident, and tailored to this role.
"""

        return self.generate(prompt)

    def generate(self, prompt):

        return f"[AI RESPONSE]\n\n{prompt}"