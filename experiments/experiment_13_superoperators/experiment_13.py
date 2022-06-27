#!/usr/bin/env python3

"""
Experiment 13 Superoperators on the binary level
"""

import logging
import os
import subprocess
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import List, Optional


NUM_INSTANCES = 10
NUM_HANDLER_TO_SAMPLE = 1000
NUM_CPUS: Optional[int] = os.cpu_count()
assert NUM_CPUS is not None, "os.cpu_count() returned None"

logger = logging.getLogger("Experiment-13")

PREFIX = Path("/home/user/evaluation/experiment_13_superoperators_binary_level")
BINARIES_DIR = PREFIX / "binaries"
SAMPLED_HANDLER_FILE = PREFIX / "sampled_handlers.txt"
EXPERIMENT_DATA_FILE = PREFIX / "synthesis_results.txt"
OBFUSCATOR_DIR = Path("../../loki/obfuscator/").resolve()
LOKIATTACK_DIR = Path("../../lokiattack/").resolve()

def setup_logging(log_level: int = logging.DEBUG) -> None:
    """Setup logger"""
    # Create handlers
    c_handler = logging.StreamHandler()  # pylint: disable=invalid-name
    f_handler = logging.FileHandler("experiment_13.log", "w+")  # pylint: disable=invalid-name
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
    logger.debug(f"Undoing patch {OBFUSCATOR_DIR.as_posix()}")
    run_cmd(cmd, OBFUSCATOR_DIR)
    # create binaries
    logger.debug("Creating binaries..")
    obfuscate_script = Path("../../loki/obfuscate.py").resolve()
    cwd = obfuscate_script.parent
    BINARIES_DIR.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "python3", obfuscate_script.as_posix(), BINARIES_DIR.as_posix(),
        "--instances", f"{NUM_INSTANCES}", "--allow", "aes_encrypt", "des_encrypt", "rc4", "md5", "sha1",
        "--nomba",
        "--verification-rounds", "1000",
        "--log-level", str(args.log_level), "--max-processes", str(args.max_processes)
    ]
    run_cmd(cmd, cwd)


def run_experiments(args: Namespace) -> None:
    handler_extract_script = LOKIATTACK_DIR / "extract_handlers.py"
    cmd = [
        "python3", handler_extract_script.as_posix(), BINARIES_DIR.as_posix(), str(NUM_HANDLER_TO_SAMPLE),
        "-o", SAMPLED_HANDLER_FILE.as_posix()
    ]
    logger.debug(f"Extracthing {NUM_HANDLER_TO_SAMPLE} handler")
    cwd = handler_extract_script.parent
    run_cmd(cmd, cwd)

    lokiattack_script = LOKIATTACK_DIR / "run.py"
    cwd = lokiattack_script.parent
    # dynamic attacker only
    logger.info("Running Syntia (program synthesis) -- dynamic attacker")
    EXPERIMENT_DATA_FILE.parent.mkdir(exist_ok=True)
    cmd = [
        "python3", lokiattack_script.as_posix(), "synthesis", BINARIES_DIR.as_posix(), "dynamic",
        "-o", EXPERIMENT_DATA_FILE.as_posix(),
        "--handler-list", SAMPLED_HANDLER_FILE.as_posix(),
        "--log-level", str(args.log_level), "--max-processes", str(args.max_processes)
    ]
    run_cmd(cmd, cwd)


def evaluate_results(_: Namespace) -> None:
    logger.info("Evaluating synthesis results -- dynamic attacker")
    eval_script = Path("./eval_synthesis.py").resolve()
    cwd = eval_script.parent
    cmd = ["python3", eval_script.as_posix(), EXPERIMENT_DATA_FILE.as_posix()]
    run_cmd(cmd, cwd)


def main(args: Namespace) -> None:
    # Step 1 build binaries
    logger.info("Building binaries")
    build_binaries(args)
    logger.info("Running experiment")
    run_experiments(args)
    logger.info("Evaluating results")
    evaluate_results(args)


if __name__ == "__main__":
    parser = ArgumentParser(description="Run experiment 13 superoperators on the binary level")
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
