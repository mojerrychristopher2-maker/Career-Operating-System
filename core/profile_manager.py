import json
from pathlib import Path


class ProfileManager:
    def __init__(self, profile_path="data/profile.json"):
        self.profile_path = Path(profile_path)
        self.profile = self.load_profile()

    def load_profile(self):
        if not self.profile_path.exists():
            raise FileNotFoundError(
                f"Profile file not found: {self.profile_path}"
            )

        with open(self.profile_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def get(self, key, default=None):
        return self.profile.get(key, default)

    def get_all(self):
        return self.profile

    def validate(self):
        required = [
            "name",
            "headline",
            "skills",
            "education",
            "experience",
            "certifications",
            "target_roles",
        ]

        missing = []

        for field in required:
            if field not in self.profile:
                missing.append(field)

        return missing