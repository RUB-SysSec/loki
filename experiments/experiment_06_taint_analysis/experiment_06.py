#!/usr/bin/env python3

"""
Experiment 06 Forward Taint Analysis (both on bit-level and byte-level)

Bit-level TA is based on Miasm
Byte-level TA is based on Triton
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

logger = logging.getLogger("Experiment-06")

PREFIX = Path("/home/user/evaluation/experiment_06_07_08_syntactic_simplification")
BINARIES_DIR = PREFIX / "binaries"
STATIC_EXPERIMENT_DATA_MIASM_FILE = PREFIX / "taint_analysis_miasm_bit_level_static.txt"
STATIC_EXPERIMENT_DATA_TRITON_FILE = PREFIX / "taint_analysis_triton_byte_level_static.txt"
DYNAMIC_EXPERIMENT_DATA_MIASM_FILE = PREFIX / "taint_analysis_miasm_bit_level_dynamic.txt"
DYNAMIC_EXPERIMENT_DATA_TRITON_FILE = PREFIX / "taint_analysis_triton_byte_level_dynamic.txt"
PATCH = Path("../../loki/obfuscator/syntactic_simplification_binaries.patch").resolve()

def setup_logging(log_level: int = logging.DEBUG) -> None:
    """Setup logger"""
    # Create handlers
    c_handler = logging.StreamHandler()
    f_handler = logging.FileHandler("experiment_06.log", "w+")
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
    # apply patch
    cmd = ["git", "apply", PATCH.as_posix()]
    cwd = PATCH.parent
    logger.debug(f"Applying patch {PATCH.as_posix()}")
    run_cmd(cmd, cwd)
    # create binaries
    logger.debug("Creating binaries..")
    obfuscate_script = Path("../../loki/obfuscate.py").resolve()
    cwd = obfuscate_script.parent
    BINARIES_DIR.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "python3", obfuscate_script.as_posix(), BINARIES_DIR.as_posix(),
        "--instances", f"{NUM_INSTANCES}", "--allow", "se_analysis", "--nosuperopt", "--deterministic",
        "--verification-rounds", "0",
        "--log-level", str(args.log_level), "--max-processes", str(args.max_processes)
    ]
    run_cmd(cmd, cwd)
    # undo patch
    cmd = ["git", "checkout", "."]
    cwd = PATCH.parent
    logger.debug(f"Undoing patch {PATCH.as_posix()}")
    run_cmd(cmd, cwd)


def run_experiments(args: Namespace) -> None:
    lokiattack_script = Path("../../lokiattack/run.py").resolve()
    cwd = lokiattack_script.parent
    # static attacker
    ## run triton byte level
    logger.info("Running Triton-based byte-level granular taint analysis -- static attacker")
    STATIC_EXPERIMENT_DATA_TRITON_FILE.parent.mkdir(exist_ok=True)
    cmd = [
        "python3", lokiattack_script.as_posix(), "taint_byte", BINARIES_DIR.as_posix(), "static",
        "-o", STATIC_EXPERIMENT_DATA_TRITON_FILE.as_posix(),
        "--log-level", str(args.log_level), "--max-processes", str(args.max_processes)
    ]
    run_cmd(cmd, cwd)
    ## run miasm bit level
    logger.info("Running Miasm-based bit-level granular taint analysis -- static attacker")
    STATIC_EXPERIMENT_DATA_MIASM_FILE.parent.mkdir(exist_ok=True)
    cmd = [
        "python3", lokiattack_script.as_posix(), "taint_bit", BINARIES_DIR.as_posix(), "static",
        "-o", STATIC_EXPERIMENT_DATA_MIASM_FILE.as_posix(),
        "--log-level", str(args.log_level), "--max-processes", str(args.max_processes)
    ]
    run_cmd(cmd, cwd)

    # dynamic attacker
    ## run triton byte level
    logger.info("Running Triton-based byte-level granular taint analysis -- dynamic attacker")
    DYNAMIC_EXPERIMENT_DATA_TRITON_FILE.parent.mkdir(exist_ok=True)
    cmd = [
        "python3", lokiattack_script.as_posix(), "taint_byte", BINARIES_DIR.as_posix(), "dynamic",
        "-o", DYNAMIC_EXPERIMENT_DATA_TRITON_FILE.as_posix(),
        "--log-level", str(args.log_level), "--max-processes", str(args.max_processes)
    ]
    run_cmd(cmd, cwd)
    ## run miasm bit level
    logger.info("Running Miasm-based bit-level granular taint analysis -- dynamic attacker")
    DYNAMIC_EXPERIMENT_DATA_MIASM_FILE.parent.mkdir(exist_ok=True)
    cmd = [
        "python3", lokiattack_script.as_posix(), "taint_bit", BINARIES_DIR.as_posix(), "dynamic",
        "-o", DYNAMIC_EXPERIMENT_DATA_MIASM_FILE.as_posix(),
        "--log-level", str(args.log_level), "--max-processes", str(args.max_processes)
    ]
    run_cmd(cmd, cwd)


def evaluate_file(file_: Path) -> None:
    eval_script = Path("./eval_taint_analysis.py").resolve()
    cwd = eval_script.parent
    cmd = ["python3", eval_script.as_posix(), file_.as_posix()]
    run_cmd(cmd, cwd)


def evaluate_results(_: Namespace) -> None:
    logger.info("Evaluating byte-granular Triton-based taint analysis results -- STATIC attacker")
    evaluate_file(STATIC_EXPERIMENT_DATA_TRITON_FILE)

    logger.info("Evaluating byte-granular Triton-based taint analysis results -- DYNAMIC attacker")
    evaluate_file(DYNAMIC_EXPERIMENT_DATA_TRITON_FILE)

    logger.info("Evaluating bit-granular Miasm-based taint analysis results -- STATIC attacker")
    evaluate_file(STATIC_EXPERIMENT_DATA_MIASM_FILE)

    logger.info("Evaluating bit-granular Miasm-based taint analysis results -- DYNAMIC attacker")
    evaluate_file(DYNAMIC_EXPERIMENT_DATA_MIASM_FILE)


def main(args: Namespace) -> None:
    # Step 1 build binaries
    logger.info("Building binaries")
    build_binaries(args)
    logger.info("Running experiment")
    run_experiments(args)
    logger.info("Evaluating results")
    evaluate_results(args)


if __name__ == "__main__":
    parser = ArgumentParser(description="Run experiment 6 taint analysis (bit-level + byte-level granularity)")
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
