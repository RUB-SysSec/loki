#!/usr/bin/env python3
"""
Parse bytecode and extract 'trace' of bytecode entries that will be executed.
"""

from argparse import ArgumentParser
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, List
import time

@dataclass
class BytecodeEntry(object):
    # path: Path
    handler_idx: int
    key: int

    def __hash__(self) -> int:
        return hash(self.handler_idx) + hash(self.key)


def parse_bytecode(path: Path) -> Iterator[bytes]:
    with open(path, 'rb') as f:
        content = f.read()
    assert len(content) % 24 == 0, f"Bytecode length should be a mulitple of 24 but is {len(content)}"
    for i in range(0, len(content), 24):
        yield content[i:i+24]


def bytecode_trace(path: Path) -> List[BytecodeEntry]:
    entries = set()
    trace = []
    handler_indices = set()
    for chunk in parse_bytecode(path / "byte_code.bin"):
        handler_idx = int.from_bytes(chunk[:2], byteorder='little')
        key = int.from_bytes(chunk[16:24], byteorder='little')
        # entry = BytecodeEntry(path, handler_idx, key)
        entry = BytecodeEntry(handler_idx, key)
        trace += [entry]
        entries.add(entry)
        handler_indices.add(handler_idx)
    return list(trace)


def main(path: Path) -> None:
    """Main"""
    start_time = time.time()
    trace = bytecode_trace(path)
    print(trace)
    print(f"[+] Done in {round(time.time() - start_time, 2)}s")


if __name__ == '__main__':
    parser = ArgumentParser(description='Bytecode trace')
    parser.add_argument('path', nargs=1, help="path to instance directory")
    args = parser.parse_args()

    target_path = Path(args.path[0]).resolve()
    main(target_path)
