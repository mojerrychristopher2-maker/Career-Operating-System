from modules.discovery.discovery_agent import DiscoveryAgent
from modules.ranking.ranking_agent import RankingAgent

jobs = DiscoveryAgent().discover_jobs()

ranked = RankingAgent().rank(jobs)

for result in ranked:

    print("=" * 50)

    print(result["job"].title)

    print("Score:", result["score"])

    print()

    for reason in result["reasons"]:
        print(reason)