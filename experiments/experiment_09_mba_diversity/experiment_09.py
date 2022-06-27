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

BINARIES_DIR_S1 = PREFIX / "binaries"
BINARIES_DIR_S2 = PREFIX / "binaries_second_set"
PATCH = Path("../../loki/obfuscator/syntactic_simplification_binaries.patch").resolve()
EXPERIMENT_DATA_FILE_S1 = PREFIX / "mba_diversity_first_set.txt"
EXPERIMENT_DATA_FILE_S2 = PREFIX / "mba_diversity_second_set.txt"


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
    # undo any modifications
    cmd = ["git", "checkout", "."]
    cwd = patch.parent
    logger.debug(f"Undoing any potential modifications")
    run_cmd(cmd, cwd)
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


def run_experiments(args: Namespace, binaries: Path, data_file: Path) -> None:
    lokiattack_script = Path("../../lokiattack/run.py").resolve()
    cwd = lokiattack_script.parent
    logger.info(f"Running mba_dump -- dynamic attacker -- results in {data_file.as_posix()}")
    data_file.parent.mkdir(exist_ok=True)
    cmd = [
        "python3", lokiattack_script.as_posix(), "mba_dump", binaries.as_posix(), "dynamic",
        "-o", data_file.as_posix(),
        "--log-level", str(args.log_level), "--max-processes", str(args.max_processes)
    ]
    run_cmd(cmd, cwd)


def evaluate_file(file_: Path, diff_to: Optional[Path]) -> None:
    eval_script = Path("./eval_mba_diversity.py").resolve()
    cwd = eval_script.parent
    cmd = ["python3", eval_script.as_posix(), file_.as_posix()]
    if diff_to is not None:
        cmd += ["--diff-to", diff_to.as_posix()]
    run_cmd(cmd, cwd)


def evaluate_results(args: Namespace, data_s1: Path, data_s2: Path) -> None:
    # logger.info("Evaluating mba diversity -- STATIC attacker")
    # evaluate_file(STATIC_EXPERIMENT_DATA_FILE)

    logger.info("Evaluating mba diversity -- DYNAMIC attacker")
    if not args.single_set:
        evaluate_file(data_s2, None)
        evaluate_file(data_s1, diff_to=data_s2)
    else:
        evaluate_file(data_s1, None)


def main(args: Namespace) -> None:
    # Step 1 build binaries
    logger.info("Building binaries")
    build_binaries(args, BINARIES_DIR_S1, PATCH)
    if not args.single_set:
        build_binaries(args, BINARIES_DIR_S2, PATCH)
    logger.info("Running experiment")
    run_experiments(args, BINARIES_DIR_S1, EXPERIMENT_DATA_FILE_S1)
    if not args.single_set:
        run_experiments(args, BINARIES_DIR_S2, EXPERIMENT_DATA_FILE_S2)
    logger.info("Evaluating results")
    evaluate_results(args, EXPERIMENT_DATA_FILE_S1, EXPERIMENT_DATA_FILE_S2)


if __name__ == "__main__":
    parser = ArgumentParser(description="Run experiment 09 MBA diversity")
    parser.add_argument("--instances", dest="num_instances", action="store", type=int, default=NUM_INSTANCES,
                        help="Number of obfuscated instances you want to generate (of the same target)")
    parser.add_argument("--log-level", dest="log_level", action="store", type=int, default=1,
                        help="Loglevel (1 = Debug, 2 = Info, 3 = Warning, 4 = Error)")
    parser.add_argument("--max-processes", dest="max_processes", action="store", type=int,
                        default=NUM_CPUS,
                        help="Number of maximal usable processes (defaults to os.cpu_count())")
    parser.add_argument("--single-set", action="store_true", default=False,
                        help="Whether to evaluate MBA diversity on only one set or compare to a second set (default)")
    cargs = parser.parse_args()

    setup_logging(cargs.log_level * 10)

    main(cargs)
