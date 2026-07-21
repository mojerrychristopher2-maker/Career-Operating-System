from core.profile_manager import ProfileManager

pm = ProfileManager()

print("Name:", pm.get("name"))
print("Headline:", pm.get("headline"))
print("Skills:", pm.get("skills"))
print("Missing:", pm.validate())