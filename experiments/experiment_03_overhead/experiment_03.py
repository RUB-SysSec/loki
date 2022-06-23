#!/usr/bin/env python3

"""
Experiment 03 Overhead of Loki's binaries (in terms of runtime and size)
"""

import json
import logging
import os
import subprocess
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import List, Optional


NUM_INSTANCES = 10
NUM_CPUS: Optional[int] = os.cpu_count()
assert NUM_CPUS is not None, "os.cpu_count() returned None"

logger = logging.getLogger("Experiment-03")

PREFIX = Path("/home/user/evaluation/experiment_01_02_03_dce/")
BINARIES_DIR = PREFIX / "binaries"
SAMPLED_HANDLER_FILE = PREFIX / "dce_handler_addresses.txt"
RUNTIME_OVERHEAD_FILE = PREFIX / "overhead_runtime.txt"
SIZE_OVERHEAD_FILE = PREFIX / "overhead_size.txt"
OBFUSCATOR_DIR = Path("../../loki/obfuscator/").resolve()
LOKIATTACK_DIR = Path("../../lokiattack/").resolve()


def setup_logging(log_level: int = logging.DEBUG) -> None:
    """Setup logger"""
    # Create handlers
    c_handler = logging.StreamHandler()  # pylint: disable=invalid-name
    f_handler = logging.FileHandler("experiment_03.log", "w+")  # pylint: disable=invalid-name
    c_handler.setLevel(log_level)
    f_handler.setLevel(log_level)
    logger.setLevel(logging.DEBUG)
    c_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    f_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s: %(message)s"))
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)


def run_cmd(cmd: List[str], cwd: Path) -> None:
    try:
        p = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=cwd)
    except subprocess.CalledProcessError as e:
        logger.error(e)
        if e.stdout:
            print(e.stdout.decode())
        exit(1)
    print(p.stdout.decode())


def build_binaries(args: Namespace) -> None:
    if BINARIES_DIR.exists():
        logger.info(
            f"Binaries directory already exists -- skipping creation of obfuscated instances -- dir is {BINARIES_DIR}"
        )
        return None
    # undo any modifications
    cmd = ["git", "checkout", "."]
    logger.debug(f"Undoing any modifications in {OBFUSCATOR_DIR.as_posix()}")
    run_cmd(cmd, OBFUSCATOR_DIR)
    # create binaries
    logger.debug("Creating binaries..")
    obfuscate_script = Path("../../loki/obfuscate.py").resolve()
    cwd = obfuscate_script.parent
    BINARIES_DIR.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "python3", obfuscate_script.as_posix(), BINARIES_DIR.as_posix(),
        "--instances", f"{NUM_INSTANCES}", "--allow", "aes_encrypt", "des_encrypt", "rc4", "md5", "sha1",
        "--verification-rounds", "1000",
        "--log-level", str(args.log_level), "--max-processes", str(args.max_processes)
    ]
    run_cmd(cmd, cwd)


def run_experiments(args: Namespace) -> None:
    # runtime overhead
    runtime_script = Path(__file__).parent / "runtime_overhead.py"
    cwd = runtime_script.parent
    logger.info("Evaluating runtime overhead")
    RUNTIME_OVERHEAD_FILE.parent.mkdir(exist_ok=True)
    cmd = [
        "python3", runtime_script.as_posix(), BINARIES_DIR.as_posix(),
        "--max-processes", str(args.max_processes)
    ]
    run_cmd(cmd, cwd)

    # size overhead
    size_script = Path(__file__).parent / "size_overhead.py"
    cwd = size_script.parent
    logger.info("Evaluating size overhead")
    SIZE_OVERHEAD_FILE.parent.mkdir(exist_ok=True)
    cmd = [
        "python3", size_script.as_posix(), BINARIES_DIR.as_posix()
    ]
    run_cmd(cmd, cwd)


def evaluate_results(_: Namespace) -> None:
    logger.debug("Please check the log files runtime_overhead.log and size_overhead.log to see the results")


def main(args: Namespace) -> None:
    # Step 1 build binaries
    logger.info("Building binaries")
    build_binaries(args)
    logger.info("Running experiment")
    run_experiments(args)
    logger.info("Evaluating results")
    evaluate_results(args)


if __name__ == "__main__":
    parser = ArgumentParser(description="Run experiment 03 overhead of Loki's binaries (in terms of runtime and size)")
    parser.add_argument("--instances", dest="num_instances", action="store", type=int, default=NUM_INSTANCES,
                        help="Number of obfuscated instances you want to generate (of the same target)")
    parser.add_argument("--log-level", dest="log_level", action="store", type=int, default=1,
                        help="Loglevel (1 = Debug, 2 = Info, 3 = Warning, 4 = Error)")
    parser.add_argument("--max-processes", dest="max_processes", action="store", type=int,
                        default=NUM_CPUS,
                        help="Number of maximal usable processes (defaults to os.cpu_count())")
    cargs = parser.parse_args()

    setup_logging(cargs.log_level * 10)

    main(cargs)
