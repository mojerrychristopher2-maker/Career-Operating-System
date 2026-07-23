from pprint import pprint

from modules.intelligence.decision_engine import DecisionEngine

engine = DecisionEngine()

print("=" * 60)
print("DECISION ENGINE")
print("=" * 60)

for score in [95, 80, 65, 45, 30]:

    print(f"\nScore: {score}")

    pprint(engine.evaluate(score))