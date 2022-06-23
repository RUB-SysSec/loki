#!/usr/bin/env python3

"""
Generate (artificial) MBA formulas for evaluation of state-of-the-art MBA
deobfuscation approaches.
"""

import os
import subprocess
from argparse import ArgumentParser, Namespace
from functools import partial
from multiprocessing import Pool
from pathlib import Path
from typing import Iterable, Iterator

OUTPUT_DIR = Path("./data")

MBA_GENERATOR_DIR = Path("../../loki/obfuscator/vm_alu").resolve()
MBA_GENERATOR = (MBA_GENERATOR_DIR.parent / "target" / "release" / "vm_alu").resolve()

# all known operations
OPS = ("+", "-", "^", "|", "&")


def build_generator() -> None:
    assert MBA_GENERATOR_DIR.is_dir(), f"MBA generator directory not found - tried '{MBA_GENERATOR_DIR.as_posix()}'"
    if not MBA_GENERATOR.is_file():
        cmd = ["cargo", "build", "--release", "--bin", "vm_alu"]
        subprocess.run(cmd, check=True, cwd=MBA_GENERATOR_DIR.as_posix())
    assert MBA_GENERATOR.is_file(), f"Failed to build MBA generator - tried '{MBA_GENERATOR.as_posix()}'"


def run_generator(op: str, cnt: int, depth: int) -> Iterator[str]:
    cmd = [MBA_GENERATOR.as_posix(), "-c", str(cnt), "-n", str(depth), "--op", op]
    p = subprocess.run(cmd, check=True, cwd=MBA_GENERATOR_DIR.parent.as_posix(), stdout=subprocess.PIPE)
    output = p.stdout.decode()
    print(output)
    mbas = [l.strip() for l in output.splitlines() if l.strip()]
    assert len(mbas) == cnt, f"Wanted {cnt} MBAs, got {len(mbas)} -- mbas: {mbas}"
    yield from mbas


def is_valid_mba(groundtruth: str, mba: str) -> bool:
    # avoid constant literals (for size guarantees)
    if "0x" in mba:
        return False
    # avoid constants
    if "c" in mba:
        return False
    # avoid key
    if "k" in mba:
        return False
    # avoid identity expressions
    if mba.replace(" ", "").strip() == groundtruth:
        return False
    return True


def generate_mba(op: str, cnt: int, depth: int) -> Iterator[str]:
    print(f"cnt={cnt}, depth={depth}, op={op}")
    assert op in OPS, f"Unsupported operation: '{op}' -- expected one of {OPS}"
    groundtruth = "x" + op + "y"
    is_valid_mba_groundtruth = partial(is_valid_mba, groundtruth)
    # lambda m: m.replace(" ", "").strip() != groundtruth and "0x" not in m
    mbas = set(filter(is_valid_mba_groundtruth, run_generator(op, cnt, depth)))
    # ensure we return exactly `cnt` MBAs
    while len(mbas) < cnt:
        new = list(filter(is_valid_mba_groundtruth, run_generator(op, cnt - len(mbas), depth)))
        mbas.update(new)
        print(f"cnt={cnt}, depth={depth}, op={op}: Having {len(mbas)} / {cnt}")
    print(f"cnt={cnt}, depth={depth}, op={op} --- DONE")
    yield from mbas


def op_to_str(op: str) -> str:
    if op == "+":
        return "add"
    if op == "-":
        return "sub"
    if op == "^":
        return "xor"
    if op == "|":
        return "or"
    if op == "&":
        return "and"
    if op == "*":
        return "mul"
    if op == "<<":
        return "shl"
    raise RuntimeError(f"Unsupported operation: '{op}' -- expected one of {OPS}")


def save_mbas(mbas: Iterable[str], op: str, depth: int, output_dir: Path) -> None:
    output_dir.mkdir(exist_ok=True)
    file_name = output_dir / f"{op_to_str(op)}_depth{depth}.txt"
    with open(file_name, "w", encoding="utf-8") as f:
        for mba in mbas:
            f.write(mba + "\n")


def process_op(op: str, cnt: int, depth: int, output_dir: Path) -> None:
    mbas = generate_mba(op, cnt, depth)
    save_mbas(mbas, op, depth, output_dir)


def generate_mbas(output_dir: Path, op: str, cnt: int, depth: int) -> None:
    assert op in OPS, \
            f"Unsupported operation: '{op}' -- expected one of {OPS}"
    process_op(op, cnt, depth, output_dir)


def generate_mbas_all_depths(output_dir: Path, op: str, cnt: int, num_jobs: int) -> None:
    with Pool(num_jobs) as pool:
        func = partial(generate_mbas, output_dir, op, cnt)
        pool.map(func, range(1,31))


def main(args: Namespace) -> None:
    build_generator()
    ops = args.ops
    if "all" in ops:
        ops = OPS
    for op in ops:
        if args.all_depths:
            generate_mbas_all_depths(args.output, op, args.count, args.max_processes)
        else:
            generate_mbas(args.output, op, args.count, args.depth)


if __name__ == "__main__":
    parser = ArgumentParser(description="Generate MBA formulas for Experiment 10 (slow!)")
    parser.add_argument("--count", "-c", default=1, type=int, help="Number of MBAs to generate and test")
    parser.add_argument("--depth", "-n", default=1, type=int, help="Recursive rewriting depth for MBA generation")
    parser.add_argument("--all-depths", dest="all_depths", action="store_true", default=False,
                        help="All depths from 1 to 30")
    parser.add_argument("--all", dest="all", action="store_true", default=False,
                        help="All depths from 1 to 30 for all operations (all possibilities)")
    parser.add_argument("--ops", nargs="+", default=["all"], type=str,
                        help="Operation from [+, -, ^, |, &, all]")
    parser.add_argument("-o", "--output", type=Path, default=OUTPUT_DIR, help="Output file where to store results")
    parser.add_argument("-j", "--max-processes", type=int, default=os.cpu_count(), help="Number of parallel jobs")
    main(parser.parse_args())
