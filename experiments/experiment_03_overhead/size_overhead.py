#!/usr/bin/python3

"""
Evaluate overhead in terms of size on disk.
"""

from argparse import ArgumentParser, Namespace
from functools import partial
from multiprocessing import Pool
from pathlib import Path
from time import time
from typing import List, Optional
import logging
import os

NUM_CPUS: Optional[int] = os.cpu_count()
MAX_PARALLEL_PROCESSES = NUM_CPUS if NUM_CPUS is not None else 4

logger = logging.getLogger("SizeOverhead")


def setup_logging(target_dir: Path) -> None:
    """Setup logger"""
    # Create handlers
    c_handler = logging.StreamHandler()
    f_handler = logging.FileHandler("size_overhead.log", "w+")
    fl_handler = logging.FileHandler(target_dir / "size_overhead.log", "w+")
    c_handler.setLevel(logging.DEBUG)
    f_handler.setLevel(logging.DEBUG)
    fl_handler.setLevel(logging.INFO)
    logger.setLevel(logging.DEBUG)
    c_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    f_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s: %(message)s"))
    fl_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s: %(message)s"))
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)
    logger.addHandler(fl_handler)


def get_size(path: Path) -> int:
    """Get size of a _file"""
    return path.stat().st_size


def enumerate_testcases(workdirs: Path, allowlist: List[str], denylist: List[str]) -> List[Path]:
    """
    Enumerate all testcases included in allowlist.
    If no allowlisted entry exists, enumerate all entries not on denylist
    """
    testcases = []
    candidates = [tc for tc in workdirs.glob("*") if tc.is_dir() and not tc.name.startswith(".")]
    if allowlist:
        testcases = [testcase for testcase in candidates if testcase.name in allowlist]
    else:
        testcases = [testcase for testcase in candidates if testcase.name not in denylist]
    logger.info(f"Found {len(testcases)} testcases")
    return testcases


def evaluate_instance(obf_name: str, instance: Path) -> int:
    """Evaluate overhead for a single instance"""
    obf_exe = (instance / obf_name)
    return get_size(obf_exe)


def avg(list_: List[int]) -> float:
    """Average value"""
    return sum(list_) / len(list_)


def evaluate_testcase(testcase_dir: Path) -> None:
    """Evaluate overhead for all instances"""
    orig_exe = testcase_dir / "bin" / "orig_exe"
    orig_size = float(get_size(orig_exe))
    instances = list((testcase_dir / "instances").glob("vm_alu*"))
    # check if we have tigress instances - TODO: improve
    if len(instances) == 0:
        instances = list((testcase_dir / "instances").glob("tigress*"))
    logger.info(f"Found {len(instances)} instances")
    with Pool(MAX_PARALLEL_PROCESSES) as pool:
        size_obf_exes = pool.map(partial(evaluate_instance, "obf_exe"), instances)
    avg_obf_size: float = avg(size_obf_exes)
    factor = avg_obf_size / orig_size
    # assert int(factor) == factor, f"{factor} cannot be converted to int"
    # logger.info(f"{testcase_dir.name}: Factor {int(factor)} (Orig: {orig_size:.2f} - Avg Obf: {avg_obf_size:.2f})")
    logger.info(
        f"{testcase_dir.name}:\n\t- obf - avg size {avg_obf_size:.2f}\n" \
        f"\t-  orig - size {orig_size:.2f}\n\t- Factor: {int(factor)}"
    )


def evaluate_themida_testcase(testcase_dir: Path) -> None:
    """Evaluate overhead for all instances"""
    orig_exe = testcase_dir / "themida" / "unobfuscated.exe"
    orig_size = float(get_size(orig_exe))
    instances = [x for x in (testcase_dir / "themida").glob("*") if x.is_dir()]
    with Pool(MAX_PARALLEL_PROCESSES) as pool:
        avg_obf_size: float = avg(pool.map(partial(evaluate_instance, "binary.exe"), instances))
    factor = avg_obf_size / orig_size
    assert int(factor) == factor, f"{factor} cannot be converted to int"
    # logger.info(f"{testcase_dir.name}: Factor {int(factor)} (Orig: {orig_size:.2f} - Avg Obf: {avg_obf_size:.2f})")
    logger.info(
        f"{testcase_dir.name}:\n\t- obf - avg size {avg_obf_size:.2f}\n" \
        f"\t- orig - size {orig_size:.2f}\n\t- Factor: {int(factor)}"
    )


def evaluate_vmprotect_testcase(testcase_dir: Path) -> None:
    """Evaluate overhead for all instances"""
    orig_exe = testcase_dir / "vmprotect" / "unobfuscated.bin"
    orig_size = float(get_size(orig_exe))
    instances = [x for x in (testcase_dir / "vmprotect").glob("*") if x.is_dir()]
    with Pool(MAX_PARALLEL_PROCESSES) as pool:
        avg_obf_size: float = avg(pool.map(partial(evaluate_instance, "obfuscated.bin"), instances))
    factor = avg_obf_size / orig_size
    assert int(factor) == factor, f"{factor} cannot be converted to int"
    # logger.info(f"{testcase_dir.name}: Factor {int(factor)} (Orig: {orig_size:.2f} - Avg Obf: {avg_obf_size:.2f})")
    logger.info(
        f"{testcase_dir.name}:\n\t- obf - avg size {avg_obf_size:.2f}\n" \
        f"\t-  orig - size {orig_size:.2f}\n\t- Factor: {int(factor)}"
    )


def main(workdirs: Path, args: Namespace) -> None: # pylint: disable = redefined-outer-name
    """
        1. Sample testcases in eval_dir
        2. For each obfuscated instance, measure overhead
    """
    start_time = time()

    testcases = enumerate_testcases(workdirs, args.allow, args.deny)

    for testcase in sorted(testcases):
        # logger.debug(f"Processing {testcase.name} ({i+1}/{len(testcases)})")
        if args.type.lower() == "themida":
            evaluate_themida_testcase(testcase)
        elif args.type.lower() == "vmprotect":
            evaluate_vmprotect_testcase(testcase)
        else:
            evaluate_testcase(testcase)
    logger.info(f"Completed {len(testcases)} testcases in {time() - start_time:0.2f}s")


if __name__ == "__main__":
    parser = ArgumentParser(description="Evaluate overhead in terms of size")
    parser.add_argument("path", type=Path, help="path to evaluation workdirs directory")
    parser.add_argument("--allow", nargs="+", default=[], help="only run specified tests")
    parser.add_argument("--deny", nargs="+", default=[],
                        help="avoid running specified tests (ignored if allowlist is specified)")
    parser.add_argument("--type", default="normal", help="specify themida or vmprotect to run")
    args = parser.parse_args()

    target_path = args.path.resolve()
    setup_logging(target_path)
    if args.type.lower() != "themida" and args.type.lower() != "vmprotect":
        target_path = target_path / "workdirs"
    main(target_path, args)
