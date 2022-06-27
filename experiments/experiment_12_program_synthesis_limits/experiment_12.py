#!/usr/bin/env python3

"""
Experiment 12 Limits of Program Synthesis
"""
import logging
import os
import subprocess
from argparse import ArgumentParser, Namespace
from pathlib import Path
import time
from typing import List, Optional


DEFAULT_MAX_DEPTH = 20
DEFAULT_NUM_EXPRESSIONS = 100
DATA_DIR = Path("/home/user/evaluation/experiment_12_synthesis_limits")

NUM_CPUS: Optional[int] = os.cpu_count()
assert NUM_CPUS is not None, "os.cpu_count() returned None"

EVAL_SCRIPT = Path("../../lokiattack/synthesis_limits.py").resolve()

logger = logging.getLogger("Experiment-12")


def setup_logging(log_level: int = logging.DEBUG) -> None:
    """Setup logger"""
    # Create handlers
    c_handler = logging.StreamHandler()  # pylint: disable=invalid-name
    f_handler = logging.FileHandler("experiment_12.log", "w+")  # pylint: disable=invalid-name
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


def run_experiment(depth: int, num_expressions: int) -> None:
    num_vars = depth if depth % 2 != 0 else depth - 1
    cmd = [
        "python3", EVAL_SCRIPT.as_posix(), str(num_vars), str(depth), str(num_expressions),
        (DATA_DIR / f"depth_{depth}.json").as_posix()
    ]
    cwd = Path("../../lokiattack").resolve()
    run_cmd(cmd, cwd)



def main(args: Namespace) -> None:
    DATA_DIR.mkdir(exist_ok=True)
    for depth in range(1, args.depth+1):
        start = time.time()
        logger.debug(f"Running for depth {depth}")
        run_experiment(depth, args.num_expressions)
        logger.debug(f"Depth {depth} done in {round(time.time() - start, 2)}s")


if __name__ == "__main__":
    parser = ArgumentParser(description="Run experiment 12 limits of program synthesis")
    parser.add_argument("--depth", type=int, default=DEFAULT_MAX_DEPTH, help="Depth until which to run experiment")
    parser.add_argument(
        "--num-expressions", type=int, default=DEFAULT_NUM_EXPRESSIONS,
        help="Number of expressions to use for synthesis for each depth (paper: 10000, default AE: 100)"
    )
    parser.add_argument(
        "--log-level", dest="log_level", action="store", type=int, default=1,
        help="Loglevel (1 = Debug, 2 = Info, 3 = Warning, 4 = Error)"
    )
    cargs = parser.parse_args()

    setup_logging(cargs.log_level * 10)

    main(cargs)
