#!/usr/bin/env python3
"""
Given an evaluation directory of the usual structure, this script extracts -- for each workdir --
all handlers with one valid key (even though multiple keys exist). Prints a list of tuples of the form:
PATH_TO_INSTANCE_DIR HANDLER_DIX KEY
This data is required for the low level synthesis evaluation where we need the correct key for the handlers.
"""

from argparse import ArgumentParser
from collections import namedtuple
from multiprocessing import Pool
from pathlib import Path
from typing import Iterator, List
import random
import time


Entry = namedtuple("Entry", "path handler_idx key")


def enumerate_testcases(workdirs: Path, allow: List[str], deny: List[str]) -> List[Path]:
    """Enumerate all testcases included in allow. If no allowed entry exists, enumerate all entries not on deny"""
    testcases = []
    candidates = [tc for tc in workdirs.glob("*") if tc.is_dir() and not tc.name.startswith(".")]
    if allow:
        testcases = [testcase for testcase in candidates if testcase.name in allow]
    else:
        testcases = [testcase for testcase in candidates if testcase.name not in deny]
    return testcases


def parse_bytecode(path: Path) -> Iterator[bytes]:
    with open(path, "rb") as f:
        content = f.read()
    assert len(content) % 24 == 0, f"Bytecode length should be a mulitple of 24 but is {len(content)}"
    for i in range(0, len(content), 24):
        yield content[i:i+24]


def collect_entry(path: Path) -> List[Entry]:
    """
    Extract handler_idx key for each handler. Ignores calls to memory handler (0x1)
    and picks the first key found for each handler. Multiple keys exist but only the
    first found key is used.
    """
    entries = set()
    handler_indices = set()
    for chunk in parse_bytecode(path / "byte_code.bin"):
        handler_idx = int.from_bytes(chunk[:2], byteorder="little")
        key = int.from_bytes(chunk[16:24], byteorder="little")
        if handler_idx == 0x1 or handler_idx in handler_indices:
            continue
        entries.add(Entry(path.as_posix(), hex(handler_idx), hex(key)))
        handler_indices.add(handler_idx)
    return list(entries)


def collect_all(path: Path) -> List[Entry]:
    """Collect reported stats"""
    instances = (path / "instances").glob("vm_alu*")
    with Pool() as pool:
        entries = pool.map(collect_entry, instances)
    flattened = set([e for sublist in entries for e in sublist])
    return list(flattened)


def sample(entries: List[Entry], num_samples: int) -> List[Entry]:
    """Randomly sample NUM_SAMPLES from all ENTRIES"""
    if num_samples > len(entries):
        print(f"Asked to sample {num_samples} but have only {len(entries)} handler")
    return random.sample(entries, num_samples)


def print_entry(entry: Entry, prefix: str = "") -> None:
    """Pretty-print Entry"""
    print(f"{prefix} {entry.path} {entry.handler_idx} {entry.key}")


def main(path: Path, num_samples: int, allow: List[str], deny: List[str], prefix: str, debug: bool) -> None:
    """Main"""
    if debug:
        start_time = time.time()
    testcases = enumerate_testcases(path / "workdirs", allow, deny)
    if debug:
        print(f"[+] Found {len(testcases)} testcases")

    entries = []
    for tc in testcases:
        entries.extend(collect_all(tc))
    if debug:
        print(f"[+] Collected {len(entries)} entries")

    # assert len(entries) == 5 * 100 * 200, f"Found {len(entries)} entries instead of 100000"
    sampled_entries = sample(entries, num_samples)
    for selected_entry in sampled_entries:
        print_entry(selected_entry, prefix)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            for e in sampled_entries:
                entry_str = f"{e.path} {e.handler_idx} {e.key}\n"
                f.write(entry_str)
    if debug:
        print(f"[+] Done in {round(time.time() - start_time, 2)}s")


if __name__ == "__main__":
    parser = ArgumentParser(description="Find all handler_idx keys in byte_code.bin and sample N random ones")
    parser.add_argument("path", nargs=1, help="path to evaluation workdirs directory")
    parser.add_argument("num_samples", nargs=1, type=int, help="number of paths to sample")
    parser.add_argument("--allow", action="store", nargs="+", default=[], help="only run specified tests")
    parser.add_argument("--deny", action="store", nargs="+", default=[],
                        help="avoid running specified tests (ignored if allowlist is specified)")
    parser.add_argument("--prefix", action="store", nargs=1, default=[""], help="prefix output with PREFIX")
    parser.add_argument("--debug", action="store_true", default=False, help="print debug output")
    parser.add_argument("-o", "--output", type=Path, help="Output file where to store results")
    args = parser.parse_args()

    target_path = Path(args.path[0]).resolve()
    main(target_path, args.num_samples[0], args.allow, args.deny, args.prefix[0], args.debug)
