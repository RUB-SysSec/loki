#!/usr/bin/env python3
"""
Given an evaluation directory of the usual structure, this script extracts
-- for each workdir -- all handler and extracts their addresses (calling to `nm`).
Output is of the following form:
PATH HANDLER_ADDR
This data is required for the deadcode elimination evaluation.
"""
from argparse import ArgumentParser, Namespace
from multiprocessing import Pool
from pathlib import Path
from os import popen
from random import sample
from typing import Iterator, List, Tuple
import time


BYTECODE_ENTRY_LENGTH = 24 # opcode (2), reg0 (2), reg1 (2), reg2 (2), imm64 (8), key (8)


def enumerate_testcases(workdirs: Path, allow: List[str], deny: List[str]) -> List[Path]:
    """
    Enumerate all testcases included in allowlist. If no allowed entry exists,
    enumerate all entries not on denylist
    """
    testcases = []
    candidates = [tc for tc in workdirs.glob("*") if tc.is_dir() and not tc.name.startswith(".")]
    if allow:
        testcases = [testcase for testcase in candidates if testcase.name in allow]
    else:
        testcases = [testcase for testcase in candidates if testcase.name not in deny]
    return testcases


def bytes_to_int(bytes_: bytes) -> int:
    """Convert bytes to integer (revert order bytewise)"""
    return int("".join([f"{b:02x}" for b in bytes_][::-1]), 16)


def chunks(list_: bytes, size: int) -> Iterator[bytes]:
    """Yield successive chunks from list (each with size 'size')."""
    for i in range(0, len(list_), size):
        yield list_[i:i + size]


def get_handler_ids(path: Path) -> Iterator[int]:
    """Get all handler IDs from bytecode"""
    with open(path, "rb") as byte_code_file:
        bytecode = byte_code_file.read()
    for handler_id in [hid[:2] for hid in chunks(bytecode, BYTECODE_ENTRY_LENGTH)]:
        yield bytes_to_int(handler_id)


def get_handler_address_mpwrapper(inp: Tuple[Path, int]) -> Tuple[Path, int]:
    """Wrap get_handler_address for multiprocessing pool use"""
    return (inp[0], get_handler_address(inp[0] / "obf_exe", inp[1]))


def get_handler_address(file_path: Path, index: int) -> int:
    """Get handler address"""
    if index == 1:
        return int(popen(f"nm {file_path.as_posix()} | grep vm_alu{index}_rrr").read().split(" ")[0], 16)
    return int(popen(f"nm {file_path.as_posix()} | grep vm_alu{index}_rrr_generated").read().split(" ")[0], 16)


def collect_directories(path: Path) -> Iterator[Path]:
    """Collect reported stats"""
    for instance in (path / "instances").glob("vm_alu*"):
        yield instance


def print_addr(path: Path, addr: int) -> None:
    """Pretty-print Entry"""
    print(f"{path} {hex(addr)}")


def main(args: Namespace) -> None:
    """Main"""
    if args.debug:
        start_time = time.time()
    testcases = enumerate_testcases(args.path.resolve() / "workdirs", args.allow, args.deny)
    if args.debug:
        print(f"[+] Found {len(testcases)} testcases")
    directories = [entry for tc in testcases for entry in collect_directories(tc)]
    if args.debug:
        print(f"[+] Collected {len(directories)} vm_alu directories")
    handler_ids = [(dir_, hid) for dir_ in directories for hid in get_handler_ids(dir_ / "byte_code.bin")]
    if args.debug:
        print(f"[+] Identified {len(handler_ids)} handler IDs")
    #handler_addresses = [(hid[0], get_handler_address(hid[0] / "obf_exe", hid[1])) for hid in handler_ids]
    if args.num_samples:
        assert args.num_samples <= len(handler_ids), \
                f"Asked for subset of {args.num_samples} but got only {len(handler_ids)} handler"
        handler_ids = sample(handler_ids, args.num_samples)
    with Pool() as pool:
        handler_addresses = pool.map(get_handler_address_mpwrapper, handler_ids)
    if args.debug:
        print(f"[+] Located {len(handler_addresses)} handler_addresses")
    for (path, addr) in handler_addresses:
        print_addr(path, addr)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            for path, addr in handler_addresses:
                entry_str = f"{path} {addr:#x}\n"
                f.write(entry_str)
    if args.debug:
        print(f"[+] Done in {round(time.time() - start_time, 2)}s")


if __name__ == "__main__":
    parser = ArgumentParser(description="Find all handler and their addresses")
    parser.add_argument("path", type=Path, help="path to evaluation workdirs directory")
    parser.add_argument("--allow", action="store", nargs="+", default=[], help="only run specified tests")
    parser.add_argument("--deny", action="store", nargs="+", default=[],
                        help="avoid running specified tests (ignored if allow is specified)")
    parser.add_argument("--debug", action="store_true", default=False, help="print debug output")
    parser.add_argument("-o", "--output", type=Path, help="Output file where to store results")
    parser.add_argument("--num-samples", type=int, default=None,
                        help="Number of handlers to randomly sample (if a subset is desired)")
    main(parser.parse_args())
