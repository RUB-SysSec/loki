#!/usr/bin/env python3

"""
Experiment 04 Key Encodings
"""

import logging
import os
import subprocess
from argparse import ArgumentParser, Namespace
from multiprocessing import Pool
from pathlib import Path
from typing import List, Optional


NUM_INSTANCES = 10
NUM_HANDLER_TO_SAMPLE = 100
NUM_CPUS: Optional[int] = os.cpu_count()
assert NUM_CPUS is not None, "os.cpu_count() returned None"

logger = logging.getLogger("Experiment-04")

PREFIX = Path("/home/user/evaluation/experiment_04_key_encodings")
FACTORIZATION_DATA_DIR = PREFIX / "factorization"
POINTFUNCTION_DATA_DIR = PREFIX / "pointfunctions"
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


def run_cmd(cmd: List[str], cwd: Path, return_output: bool = False) -> Optional[str]:
    try:
        p = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=cwd)
    except subprocess.CalledProcessError as e:
        logger.error(e)
        if e.stdout:
            print(e.stdout.decode())
        exit(1)
    if return_output:
        return p.stdout.decode()
    print(p.stdout.decode())
    return None


def generate_encoding(args: Namespace, data_file_dir: Path, ty: str) -> None:
    if data_file_dir.exists():
        logger.info(
            f"Encodings already generated -- skipping creation -- dir is {data_file_dir.as_posix()}"
        )
        return None
    data_file_dir.mkdir(exist_ok=True)
    # create binaries
    logger.debug(f"Creating {args.num_instances} {ty} encodings..")
    eval_smt_bin = OBFUSCATOR_DIR / "target" / "release" / "eval_smt"
    assert eval_smt_bin.exists(), f"Failed to build {eval_smt_bin.as_posix()}"
    for i in range(args.num_instances):
        cmd = [
            eval_smt_bin.as_posix(), ty
        ]
        output = run_cmd(cmd, OBFUSCATOR_DIR, return_output=True)
        # print(f"output={output}")
        assert output is not None, "No output returned :("
        data_file = data_file_dir / f"{ty}_{i}.txt"
        with open(data_file, "w", encoding="utf-8") as f:
            f.write(output.strip() + "\n")


def generate_encodings(args: Namespace) -> None:
    # undo any modifications
    cmd = ["git", "checkout", "."]
    logger.debug(f"Undoing patch {OBFUSCATOR_DIR.as_posix()}")
    run_cmd(cmd, OBFUSCATOR_DIR)
    # build
    logger.debug("Building binary")
    PREFIX.mkdir(parents=True, exist_ok=True)
    cmd = [
        "cargo", "build", "--release", "--bin", "eval_smt"
    ]
    run_cmd(cmd, OBFUSCATOR_DIR)
    generate_encoding(args, FACTORIZATION_DATA_DIR, "factorization")
    generate_encoding(args, POINTFUNCTION_DATA_DIR, "pointfunction")


def test_encoding(encoding_file: Path) -> str:
    # with open(encoding_file, "r", encoding="utf-8") as f:
    #     encoding = f.read().strip()
    solver_script = Path("./solve.py")
    cmd = [
        "python3", solver_script.as_posix(), encoding_file.as_posix()
    ]
    output = run_cmd(cmd, solver_script.parent, return_output=True)

    assert output is not None
    output = output.strip()
    return output


def run_experiment(_: Namespace, data_file_dir: Path, ty: str) -> None:
    logger.info(f"Using CEGAR approach on {ty} encodings")
    files = list(data_file_dir.glob(f"{ty}_*.txt"))
    # results = []
    # for f in files:
    #     results.append(test_encoding(f))
    with Pool() as pool:
        results = pool.map(test_encoding, files)
    # save results
    results_file = PREFIX / f"results_{ty}.txt"
    with open(results_file, "w", encoding="utf-8") as fd:
        fd.write("\n".join(results) + "\n")
    # print some stats
    solved = len(list(filter(lambda r: r.startswith("solved"), results)))
    not_solved = len(list(filter(lambda r: r.startswith("not solved"), results)))
    assert solved + not_solved == len(results)
    assert len(files) == len(results)
    percentage = round(100 * solved / len(files), 2)
    logger.info(f"{ty}: solved {solved} / {len(files)} ({percentage}%)")



def run_experiments(args: Namespace) -> None:
    run_experiment(args, FACTORIZATION_DATA_DIR, "factorization")
    run_experiment(args, POINTFUNCTION_DATA_DIR, "pointfunction")


def main(args: Namespace) -> None:
    # Step 1 build binaries
    logger.info("Generating binaries")
    generate_encodings(args)
    logger.info("Running experiment")
    run_experiments(args)


if __name__ == "__main__":
    parser = ArgumentParser(description="Run experiment 13 superoperators on the binary level")
    parser.add_argument("--num-encodings", dest="num_instances", action="store", type=int, default=NUM_INSTANCES,
                        help="Number of key encodings you want to generate (for each type)")
    parser.add_argument("--log-level", dest="log_level", action="store", type=int, default=1,
                        help="Loglevel (1 = Debug, 2 = Info, 3 = Warning, 4 = Error)")
    parser.add_argument("--max-processes", dest="max_processes", action="store", type=int,
                        default=NUM_CPUS,
                        help="Number of maximal usable processes (defaults to os.cpu_count())")
    cargs = parser.parse_args()

    setup_logging(cargs.log_level * 10)

    main(cargs)
