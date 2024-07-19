import argparse
from .freeze import freeze


def cli():
    parser = argparse.ArgumentParser(
        description="Pub/Sub consumer common.",
    )
    subparsers = parser.add_subparsers(
        dest="command",
    )

    freeze(subparsers)

    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
        return

    parser.print_help()
