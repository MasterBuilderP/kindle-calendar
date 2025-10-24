from .cache import cache
from .cal_sources.evolution import get_events as get_events_evolution

sources = [get_events_evolution]


def main():
    existing = cache().keys()
    data = {}
    for source in sources:
        data.update(source())
    all = cache(data).keys()

    new = all - existing
    if len(new) > 0:
        print(f"Found {len(new)} new events")

    cleaned = existing - all
    if len(cleaned) > 0:
        print(f"Cleaned up {len(cleaned)} events")
