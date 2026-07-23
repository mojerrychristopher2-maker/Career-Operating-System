from knowledge.skill_graph import SkillGraph

graph = SkillGraph()

profile = [

    "Python",
    "SQL",
    "Power BI",
    "Excel",
    "Git"

]

print("=" * 60)

print("Business Intelligence")

print(graph.satisfies(profile, "Business Intelligence"))

print()

print("Azure")

print(graph.satisfies(profile, "Azure"))

print()

print("SQL")

print(graph.satisfies(profile, "SQL"))