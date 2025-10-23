import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="command", description="Example CLI tool")
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    parser_cache = subparsers.add_parser("cache", help="Cache tool")
    parser_cache_subs = parser_cache.add_subparsers(dest="cache_action", required=True)

    parser_cache_subs.add_parser("ls", help="List items")

    parser_del = parser_cache_subs.add_parser("del", help="Delete an item by ID")
    parser_del.add_argument("id", type=int, help="ID of the item to delete")

    parser_render = subparsers.add_parser("render", help="Render calendar screen")
    parser_render.add_argument("filename", help="Path to the output file")
    parser_render.add_argument("--kindle", action="store_true", help="Use kindle fonts")

    subparsers.add_parser("calendar")

    args = parser.parse_args()

    if args.subcommand == "cache":
        from .cache import main

        main(args)
    elif args.subcommand == "calendar":
        from .calendar import main

        main()
    elif args.subcommand == "render":
        from .render import main

        main(args)
