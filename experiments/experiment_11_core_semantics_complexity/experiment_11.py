#!/usr/bin/env python3

"""
Experiment 11 Complexity of Core Semantics
"""
import logging
import os
import subprocess
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import List, Optional


NUM_INSTANCES = 10
NUM_CPUS: Optional[int] = os.cpu_count()
assert NUM_CPUS is not None, "os.cpu_count() returned None"

logger = logging.getLogger("Experiment-11")

PREFIX = Path("/home/user/evaluation/experiment_11_complexity_of_core_semantics")

BINARIES_DIR = PREFIX / "binaries_no_superoperator"
BINARIES_SUPEROPT_DIR = PREFIX / "binaries_with_superoperator"
PATCH = Path("../../loki/obfuscator/core_semantics_complexity.patch").resolve()



def setup_logging(log_level: int = logging.DEBUG) -> None:
    """Setup logger"""
    # Create handlers
    c_handler = logging.StreamHandler()  # pylint: disable=invalid-name
    f_handler = logging.FileHandler("experiment_11.log", "w+")  # pylint: disable=invalid-name
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
    # apply patch
    cmd = ["git", "apply", PATCH.as_posix()]
    cwd = PATCH.parent
    logger.debug(f"Applying patch {PATCH.as_posix()}")
    run_cmd(cmd, cwd)
    # create binaries
    logger.debug("Creating binaries..")
    obfuscate_script = Path("../../loki/obfuscate.py").resolve()
    cwd = obfuscate_script.parent
    if BINARIES_DIR.exists():
        logger.info(
            f"Binaries directory already exists -- skipping creation of obfuscated instances -- dir is {BINARIES_DIR}"
        )
    else:
        logger.info("Building binaries without superoperators")
        BINARIES_DIR.parent.mkdir(parents=True, exist_ok=True)
        cmd = [
            "python3", obfuscate_script.as_posix(), BINARIES_DIR.as_posix(),
            "--instances", f"{NUM_INSTANCES}", "--allow", "aes_encrypt", "des_encrypt", "md5", "rc4", "sha1",
            "--no-generate-vm", "--nomba", "--nosuperopt",
            "--verification-rounds", "0",
            "--log-level", str(args.log_level), "--max-processes", str(args.max_processes)
        ]
        run_cmd(cmd, cwd)
    if BINARIES_SUPEROPT_DIR.exists():
        logger.info(
            f"Binaries w/ superoperators directory already exists -- skipping creation of obfuscated instances " \
            f"-- dir is {BINARIES_SUPEROPT_DIR}"
        )
    else:
        logger.info("Building binaries with superoperators")
        BINARIES_DIR.parent.mkdir(parents=True, exist_ok=True)
        cmd = [
            "python3", obfuscate_script.as_posix(), BINARIES_SUPEROPT_DIR.as_posix(),
            "--instances", f"{NUM_INSTANCES}", "--allow", "aes_encrypt", "des_encrypt", "md5", "rc4", "sha1",
            "--no-generate-vm", "--nomba",
            "--verification-rounds", "0",
            "--log-level", str(args.log_level), "--max-processes", str(args.max_processes)
        ]
        run_cmd(cmd, cwd)
    # undo patch
    cmd = ["git", "checkout", "."]
    cwd = PATCH.parent
    logger.debug(f"Undoing patch {PATCH.as_posix()}")
    run_cmd(cmd, cwd)


def run_experiments(_: Namespace) -> None:
    cmd = ["python3", "eval_complexity.py", BINARIES_DIR.as_posix(), BINARIES_SUPEROPT_DIR.as_posix()]
    cwd = Path(__file__).parent
    run_cmd(cmd, cwd)


def evaluate_results(_: Namespace) -> None:
    pass


def main(args: Namespace) -> None:
    logger.info("Creating data")
    build_binaries(args)
    logger.info("Running experiment")
    run_experiments(args)
    logger.info("Evaluating results")
    evaluate_results(args)


if __name__ == "__main__":
    parser = ArgumentParser(description="Run experiment 11 complexity of core semantics")
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
