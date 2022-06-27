#!/usr/bin/env python3

"""
Experiment 08 Symbolic Execution

This must create two sets of binaries, once having core semantics with depth 3 and once with depth 5.
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

logger = logging.getLogger("Experiment-08")

PREFIX = Path("/home/user/evaluation/experiment_06_07_08_syntactic_simplification")

BINARIES_DIR = PREFIX / "binaries"
PATCH = Path("../../loki/obfuscator/syntactic_simplification_binaries.patch").resolve()
STATIC_EXPERIMENT_DATA_FILE = PREFIX / "symbolic_execution_static.txt"
DYNAMIC_EXPERIMENT_DATA_FILE = PREFIX / "symbolic_execution_dynamic.txt"

DEPTH_5_BINARIES_DIR = PREFIX / "binaries_depth_5"
DEPTH_5_PATCH = Path("../../loki/obfuscator/syntactic_simplification_binaries_depth_5.patch").resolve()
DEPTH_5_STATIC_EXPERIMENT_DATA_FILE = PREFIX / "symbolic_execution_depth_5_static.txt"
DEPTH_5_DYNAMIC_EXPERIMENT_DATA_FILE = PREFIX / "symbolic_execution_depth_5_dynamic.txt"



def setup_logging(log_level: int = logging.DEBUG) -> None:
    """Setup logger"""
    # Create handlers
    c_handler = logging.StreamHandler()  # pylint: disable=invalid-name
    f_handler = logging.FileHandler("experiment_08.log", "w+")  # pylint: disable=invalid-name
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


def build_binaries(args: Namespace, binaries_dir: Path, patch: Path, use_superops: bool) -> None:
    if binaries_dir.exists():
        logger.info(
            f"Binaries directory already exists -- skipping creation of obfuscated instances -- dir is {binaries_dir}"
        )
        return None
    cmd = ["git", "checkout", "."]
    cwd = patch.parent
    logger.debug("Undoing any potential modification")
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
        "--instances", f"{NUM_INSTANCES}", "--allow", "se_analysis", "--deterministic",
        "--verification-rounds", "0",
        "--log-level", str(args.log_level), "--max-processes", str(args.max_processes)
    ]
    if not use_superops:
        cmd += [ "--nosuperopt", ]
    run_cmd(cmd, cwd)
    # undo patch
    cmd = ["git", "checkout", "."]
    cwd = patch.parent
    logger.debug(f"Undoing patch {patch.as_posix()}")
    run_cmd(cmd, cwd)


def run_experiments(args: Namespace, binaries_dir: Path, static_file: Path, dynamic_file: Path, depth: int) -> None:
    lokiattack_script = Path("../../lokiattack/run.py").resolve()
    cwd = lokiattack_script.parent
    # static attacker
    logger.info(f"Running symbolic_execution depth {depth} -- static attacker")
    static_file.parent.mkdir(exist_ok=True)
    if depth == 3:
        plugin = "symbolic_execution"
    elif depth == 5:
        plugin = "se_depth_5"
    else:
        raise RuntimeError(f"Unsupported depth {depth} (expected 3 or 5)")
    cmd = [
        "python3", lokiattack_script.as_posix(), plugin, binaries_dir.as_posix(), "static",
        "-o", static_file.as_posix(),
        "--log-level", str(args.log_level), "--max-processes", str(args.max_processes)
    ]
    run_cmd(cmd, cwd)
    # dynamic attacker
    logger.info(f"Running symbolic_execution depth {depth} -- dynamic attacker")
    dynamic_file.parent.mkdir(exist_ok=True)
    cmd = [
        "python3", lokiattack_script.as_posix(), plugin, binaries_dir.as_posix(), "dynamic",
        "-o", dynamic_file.as_posix(),
        "--log-level", str(args.log_level), "--max-processes", str(args.max_processes)
    ]
    run_cmd(cmd, cwd)


def evaluate_file(file_: Path) -> None:
    eval_script = Path("./eval_symbolic_execution.py").resolve()
    cwd = eval_script.parent
    cmd = ["python3", eval_script.as_posix(), file_.as_posix()]
    run_cmd(cmd, cwd)


def evaluate_results(_: Namespace, static_file: Path, dynamic_file: Path, depth: int) -> None:
    logger.info(f"Evaluating symbolic_execution depth {depth} -- STATIC attacker")
    evaluate_file(static_file)

    logger.info(f"Evaluating symbolic_execution depth {depth} -- DYNAMIC attacker")
    evaluate_file(dynamic_file)


def main(args: Namespace) -> None:
    # Step 1 build binaries
    logger.info("Building binaries depth 3")
    build_binaries(args, BINARIES_DIR, PATCH, use_superops=False)
    logger.info("Building binaries depth 5")
    build_binaries(args, DEPTH_5_BINARIES_DIR, DEPTH_5_PATCH, use_superops=True)
    logger.info("Running experiment depth 3")
    run_experiments(args, BINARIES_DIR, STATIC_EXPERIMENT_DATA_FILE, DYNAMIC_EXPERIMENT_DATA_FILE, 3)
    logger.info("Running experiment depth 5")
    run_experiments(
        args, DEPTH_5_BINARIES_DIR, DEPTH_5_STATIC_EXPERIMENT_DATA_FILE, DEPTH_5_DYNAMIC_EXPERIMENT_DATA_FILE, 5
    )
    logger.info("Evaluating results depth 3")
    evaluate_results(args, STATIC_EXPERIMENT_DATA_FILE, DYNAMIC_EXPERIMENT_DATA_FILE, 3)
    logger.info("Evaluating results depth 5")
    evaluate_results(args, DEPTH_5_STATIC_EXPERIMENT_DATA_FILE, DEPTH_5_DYNAMIC_EXPERIMENT_DATA_FILE, 5)


if __name__ == "__main__":
    parser = ArgumentParser(description="Run experiment 08 symbolic_execution")
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
