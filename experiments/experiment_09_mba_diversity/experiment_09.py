#!/usr/bin/env python3

"""
Experiment 09 MBA diversity
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

logger = logging.getLogger("Experiment-09")

PREFIX = Path("/home/user/evaluation/experiment_06_07_08_syntactic_simplification")

BINARIES_DIR = PREFIX / "binaries"
PATCH = Path("../../loki/obfuscator/syntactic_simplification_binaries.patch").resolve()
STATIC_EXPERIMENT_DATA_FILE = PREFIX / "mba_diversity_static.txt"
DYNAMIC_EXPERIMENT_DATA_FILE = PREFIX / "mba_diversity_dynamic.txt"


def setup_logging(log_level: int = logging.DEBUG) -> None:
    """Setup logger"""
    # Create handlers
    c_handler = logging.StreamHandler()  # pylint: disable=invalid-name
    f_handler = logging.FileHandler("experiment_09.log", "w+")  # pylint: disable=invalid-name
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


def build_binaries(args: Namespace, binaries_dir: Path, patch: Path) -> None:
    if binaries_dir.exists():
        logger.info(
            f"Binaries directory already exists -- skipping creation of obfuscated instances -- dir is {binaries_dir}"
        )
        return None
    # apply patch
    cmd = ["git", "apply", patch.as_posix()]
    cwd = patch.parent
    logger.debug(f"Applying patch {patch.as_posix()}")
    run_cmd(cmd, cwd)
    # create binaries
    logger.debug("Creating binaries..")
    obfuscate_script = Path("../../loki/obfuscate.py").resolve()
    cwd = obfuscate_script.parent
    binaries_dir.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "python3", obfuscate_script.as_posix(), binaries_dir.as_posix(),
        "--instances", f"{NUM_INSTANCES}", "--allow", "se_analysis", "--nosuperopt", "--deterministic",
        "--verification-rounds", "0",
        "--log-level", str(args.log_level), "--max-processes", str(args.max_processes)
    ]
    run_cmd(cmd, cwd)
    # undo patch
    cmd = ["git", "checkout", "."]
    cwd = patch.parent
    logger.debug(f"Undoing patch {patch.as_posix()}")
    run_cmd(cmd, cwd)


def run_experiments(args: Namespace) -> None:
    lokiattack_script = Path("../../lokiattack/run.py").resolve()
    cwd = lokiattack_script.parent
    # # static attacker
    # logger.info(f"Running mba_dump -- static attacker")
    # STATIC_EXPERIMENT_DATA_FILE.parent.mkdir(exist_ok=True)
    # cmd = [
    #     "python3", lokiattack_script.as_posix(), "mba_dump", BINARIES_DIR.as_posix(), "static",
    #     "-o", STATIC_EXPERIMENT_DATA_FILE.as_posix(),
    #     "--log-level", str(args.log_level), "--max-processes", str(args.max_processes)
    # ]
    # run_cmd(cmd, cwd)
    # dynamic attacker
    logger.info(f"Running mba_dump -- dynamic attacker")
    DYNAMIC_EXPERIMENT_DATA_FILE.parent.mkdir(exist_ok=True)
    cmd = [
        "python3", lokiattack_script.as_posix(), "mba_dump", BINARIES_DIR.as_posix(), "dynamic",
        "-o", DYNAMIC_EXPERIMENT_DATA_FILE.as_posix(),
        "--log-level", str(args.log_level), "--max-processes", str(args.max_processes)
    ]
    run_cmd(cmd, cwd)


def evaluate_file(file_: Path) -> None:
    eval_script = Path("./eval_mba_diversity.py").resolve()
    cwd = eval_script.parent
    cmd = ["python3", eval_script.as_posix(), file_.as_posix()]
    run_cmd(cmd, cwd)


def evaluate_results(_: Namespace) -> None:
    # logger.info("Evaluating mba diversity -- STATIC attacker")
    # evaluate_file(STATIC_EXPERIMENT_DATA_FILE)

    logger.info("Evaluating mba diversity -- DYNAMIC attacker")
    evaluate_file(DYNAMIC_EXPERIMENT_DATA_FILE)


def main(args: Namespace) -> None:
    # Step 1 build binaries
    logger.info("Building binaries")
    build_binaries(args, BINARIES_DIR, PATCH)
    logger.info("Running experiment")
    run_experiments(args)
    logger.info("Evaluating results")
    evaluate_results(args)


if __name__ == "__main__":
    parser = ArgumentParser(description="Run experiment 09 MBA diversity")
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
