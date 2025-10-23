from .cache import cache
from .cal_sources.evolution import get_events


def main():
    existing = len(cache())
    events = len(get_events())
    if events > existing:
        print(f"Found {events - existing} new events")
