import argparse, json, time
from agent.config import settings
from agent.store import Store
from agent.workers import CareerWorkers

def profile():
    if not settings.profile.exists(): raise RuntimeError('Create data/profile.json from data/profile.example.json first.')
    return json.loads(settings.profile.read_text(encoding='utf-8'))
def run_cycle(store, workers):

    jobs = workers.discovery.discover()

    workers.process(profile(), jobs)

    store.log(
        "cycle",
        f"Completed autonomous cycle; {len(jobs)} jobs discovered."
    )

    print(
        f"Cycle complete. {len(jobs)} jobs discovered."
    )
def main():
    parser=argparse.ArgumentParser(description='Mojerry Career OS autonomous worker')
    parser.add_argument('command',choices=['run-once','watch','status']); args=parser.parse_args(); store=Store(settings.database)
    if args.command=='status':
        for row in store.db.execute('select status,count(*) total from jobs group by status'): print(f"{row['status']}: {row['total']}")
        return
    workers=CareerWorkers(store,settings)
    if args.command=='run-once': run_cycle(store,workers)
    else:
        while True:
            try: run_cycle(store,workers)
            except Exception as e: store.log('error',str(e)); print(f'Cycle failed: {e}')
            time.sleep(settings.poll_seconds)
if __name__=='__main__': main()
