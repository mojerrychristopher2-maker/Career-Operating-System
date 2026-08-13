import json

path = "data/profile.json"

with open(path, "r", encoding="utf-8") as f:
    data = json.load(f)

h = "".join(map(chr, [104,116,116,112,115,58,47,47]))

greenhouse = h + "boards.greenhouse.io/anthropic"
lever = h + "jobs.lever.co/gohighlevel"

data["career_sites"] = [greenhouse, lever]

with open(path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print("FIXED:")
for site in data["career_sites"]:
    print(repr(site))