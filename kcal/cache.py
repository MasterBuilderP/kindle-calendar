import json
import uuid
from datetime import datetime

event_cache_path = "event_cache.json"


def encode(data):
    return {
        k: {
            vk: {
                **vv,
                "start_dt": vv["start_dt"].isoformat(),
                "end_dt": vv["end_dt"].isoformat(),
            }
            for vk, vv in v.items()
        }
        for k, v in data.items()
    }


def clean(data):
    now = datetime.now().astimezone()
    return {
        k: {vk: vv for vk, vv in v.items() if vv["end_dt"] > now}
        for k, v in data.items()
    }


def decode(data):
    return {
        k: {
            vk: {
                **vv,
                "start_dt": datetime.fromisoformat(vv["start_dt"]),
                "end_dt": datetime.fromisoformat(vv["end_dt"]),
            }
            for vk, vv in v.items()
        }
        for k, v in data.items()
    }


def merge(data):
    # If identical events from two devices exist, the last one added will be used
    return {vk: vv for _, v in data.items() for vk, vv in v.items()}


def cache(new_data=None):
    try:
        with open(event_cache_path) as f:
            data = clean(decode(json.load(f)))
    except FileNotFoundError:
        data = {}

    if new_data:
        data[str(uuid.getnode())] = new_data

        with open(event_cache_path, "w") as f:
            json.dump(encode(data), f)

    return merge(data)


def main(args):
    data = cache()
    if args.cache_action == "ls":
        for i, k in enumerate(data.keys()):
            item = data[k]
            print(f"{i}: {item['start_dt'].isoformat()} {item['summary']}")
    elif args.cache_action == "del":
        if 0 <= args.id < len(data.keys()):
            data.pop(list(data.keys())[args.id], None)
            with open(event_cache_path, "w") as f:
                json.dump(encode(data), f)
