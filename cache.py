import json
from datetime import datetime


def encode(data):
    return {
        k: {
            **v,
            "start_dt": v["start_dt"].isoformat(),
            "end_dt": v["end_dt"].isoformat(),
        }
        for k, v in data.items()
    }


def clean(data):
    now = datetime.now().astimezone()
    return {k: v for k, v in data.items() if v["end_dt"] > now}


def decode(data):
    return {
        k: {
            **v,
            "start_dt": datetime.fromisoformat(v["start_dt"]),
            "end_dt": datetime.fromisoformat(v["end_dt"]),
        }
        for k, v in data.items()
    }


def cache(new_data=None):
    event_cache_path = "event_cache.json"
    try:
        with open(event_cache_path) as f:
            data = clean(decode(json.load(f)))
    except FileNotFoundError:
        data = {}

    if new_data:
        data.update(new_data)

        with open(event_cache_path, "w") as f:
            json.dump(encode(data), f)

    return data
