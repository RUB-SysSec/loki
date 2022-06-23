#!/usr/bin/env python3
"""
Evaluate results of Experiment 9 MBA diversity

How many unique MBAs are there?
"""

from argparse import ArgumentParser, Namespace
from pathlib import Path

def main(args: Namespace) -> None:
    with open(args.path, "r", encoding="utf-8") as f:
        content = [l.strip() for l in f.readlines() if l]
    unique_mbas = set(content)
    print(f"Found {len(content)} MBAs")
    print(f"Found {len(unique_mbas)} unique MBAs")
    print(unique_mbas)
    if args.diff_to:
        with open(args.diff_to, "r", encoding="utf-8") as f:
            content_2 = [l.strip() for l in f.readlines() if l]
        unique_mbas_2 = set(content_2)
        print(f"Found {len(unique_mbas.difference(unique_mbas_2))} unique MBAs"\
              f" in {args.path.name} that are not in {args.diff_to.name}")

if __name__ == "__main__":
    parser = ArgumentParser(description="Evaluate number of unique MBAs")
    parser.add_argument("path", type=Path, help="Path to results file produced by LokiAttack with mba_dumper plugin")
    parser.add_argument("--diff-to", type=Path, help="Second results file which you want to check difference to")
    main(parser.parse_args())
