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
    print(f"{args.path.name}: Found {len(content)} MBAs")
    percentage = round(100 * len(unique_mbas) / len(content), 2)
    print(f"{args.path.name}: Found {len(unique_mbas)} unique MBAs ({percentage}%)")
    # print(unique_mbas)
    if args.diff_to:
        with open(args.diff_to, "r", encoding="utf-8") as f:
            content_2 = [l.strip() for l in f.readlines() if l]
        unique_mbas_2 = set(content_2)
        difference = len(unique_mbas.difference(unique_mbas_2))
        percentage_diff = round(100 * difference / len(unique_mbas), 2)
        print(
            f"{args.path.name}: Found {difference} unique MBAs in {args.path.name} " \
            f"that are not in {args.diff_to.name} ({percentage_diff}%)")

if __name__ == "__main__":
    parser = ArgumentParser(description="Evaluate number of unique MBAs")
    parser.add_argument("path", type=Path, help="Path to results file produced by LokiAttack with mba_dumper plugin")
    parser.add_argument("--diff-to", type=Path, help="Second results file which you want to check difference to")
    main(parser.parse_args())
