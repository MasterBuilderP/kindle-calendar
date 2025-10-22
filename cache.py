import json
from datetime import datetime

event_cache_path = "event_cache.json"


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


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Cache helper")
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    parser_ls = subparsers.add_parser("ls", help="List items")

    parser_del = subparsers.add_parser("del", help="Delete an item by ID")
    parser_del.add_argument("id", type=int, help="ID of the item to delete")

    args = parser.parse_args()

    data = cache()
    if args.subcommand == "ls":
        for i, k in enumerate(data.keys()):
            item = data[k]
            print(f"{i}: {item['start_dt'].isoformat()} {item['summary']}")
    elif args.subcommand == "del":
        if 0 <= args.id < len(data.keys()):
            data.pop(list(data.keys())[args.id], None)
            with open(event_cache_path, "w") as f:
                json.dump(encode(data), f)
