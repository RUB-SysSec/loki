#!/usr/bin/env python3
"""
Get executed and unique executed handlers
"""

from argparse import ArgumentParser
from pathlib import Path
from typing import Set, Tuple


def count_handlers(file_path: Path) -> Tuple[int, int]:
    """
    Iterate over bytecode bin file and inspect each handler
    Return total number of handlers executed and unique handlers executed
    """
    with open(file_path, "rb") as f:
        content = f.read()
    seen: Set[bytes] = set()
    num_executed_handlers = 0
    offset = 0
    while offset < len(content):
        num_executed_handlers += 1
        hander_index = content[offset:offset + 2][::-1]
        seen.add(hander_index)
        offset += 24
    return num_executed_handlers, len(seen)


def main(path: Path) -> None:
    num_files = 0
    num_executed_handlers = 0
    num_unique_executed_handlers = 0
    for file_path in path.glob("workdirs/*/instances/vm_alu*/byte_code.bin"):
        num_files += 1
        # parse file
        executed, unique = count_handlers(file_path)
        # update global stats
        num_executed_handlers += executed
        num_unique_executed_handlers += unique
    print(f"total number of executed handlers: {num_executed_handlers/num_files}")
    print(f"total number of uniquely executed handlers: {num_unique_executed_handlers/num_files}")


if __name__ == "__main__":
    parser = ArgumentParser(description="Get Loki's executed and unique executed handlers")
    parser.add_argument("path", type=Path, help="path to evaluation directory")

    main(parser.parse_args().path)
