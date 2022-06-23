#!/usr/bin/env python3

"""
Experiment 10 MBA Formula Deobfuscation
"""

import logging
import os
import subprocess
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Dict, List, Optional


NUM_FORMULAS = 10
NUM_CPUS: Optional[int] = os.cpu_count()
assert NUM_CPUS is not None, "os.cpu_count() returned None"

logger = logging.getLogger("Experiment-10")

PREFIX = Path("/home/user/evaluation/experiment_10_mba_formulas").resolve()
DEOBFUSCATION_TOOLS = Path("./deobfuscation_tools").resolve()
MBAS_DIR = PREFIX / "mba_formulas"
EXPERIMENT_DATA = PREFIX / "experiment_data"
OBFUSCATOR_DIR = Path("../../loki/obfuscator/").resolve()
LOKIATTACK_DIR = Path("../../lokiattack/").resolve()

PATCH = OBFUSCATOR_DIR / "mba_formula_generation.patch"


def setup_logging(log_level: int = logging.DEBUG) -> None:
    """Setup logger"""
    # Create handlers
    c_handler = logging.StreamHandler()  # pylint: disable=invalid-name
    f_handler = logging.FileHandler("experiment_10.log", "w+")  # pylint: disable=invalid-name
    c_handler.setLevel(log_level)
    f_handler.setLevel(log_level)
    logger.setLevel(logging.DEBUG)
    c_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    f_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s: %(message)s"))
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)


def run_cmd(cmd: List[str], cwd: Path, env: Optional["os._Environ[str]"] = None) -> None:
    try:
        if env is not None:
            print(f"env={env}")
            p = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=cwd, env=env)
        else:
            p = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=cwd)
    except subprocess.CalledProcessError as e:
        logger.error(e)
        if e.stdout:
            print(e.stdout.decode())
        exit(1)
    print(p.stdout.decode())


def create_formulas(args: Namespace) -> None:
    if MBAS_DIR.exists():
        logger.info(
            f"Formulas directory already exists -- skipping creation of MBA formulas -- dir is {MBAS_DIR}"
        )
        return None
    # undo any modifications
    cmd = ["git", "checkout", "."]
    logger.debug(f"Undoing patch {OBFUSCATOR_DIR.as_posix()}")
    run_cmd(cmd, OBFUSCATOR_DIR)
    # undo any modifications
    cmd = ["git", "apply", PATCH.as_posix()]
    logger.debug(f"Applying patch {PATCH.as_posix()}")
    run_cmd(cmd, OBFUSCATOR_DIR)
    # create binaries
    logger.debug("Creating formulas..")
    generate_script = Path("generate_mba_formulas.py").resolve()
    cwd = generate_script.parent
    MBAS_DIR.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "python3", generate_script.as_posix(),
        "-j", args.max_processes,
        "-c", str(NUM_FORMULAS),
        "-o", MBAS_DIR.as_posix(),
        "--ops" , "+", "-", "|", "&", "^"
    ]
    run_cmd(cmd, cwd)


def sample_formulas(_: Namespace) -> None:
    if MBAS_DIR.exists():
        logger.info(
            f"Formulas directory already exists -- skipping sampling of MBAs -- dir is {MBAS_DIR}"
        )
        return None
    logger.debug(f"Sampling {NUM_FORMULAS} formulas..")
    sample_script = Path("sample_formulas.py").resolve()
    cwd = sample_script.parent
    MBAS_DIR.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "python3", sample_script.as_posix(),
        str(NUM_FORMULAS),
        MBAS_DIR.as_posix()
    ]
    run_cmd(cmd, cwd)


def run_lokiattack_experiment(args: Namespace) -> None:
    if (EXPERIMENT_DATA / "lokiattack_data").exists():
        logger.info(f"{EXPERIMENT_DATA / 'lokiattack_data'} exists -- will not run LokiAttack again")
        return

    # run LokiAttack
    EXPERIMENT_DATA.mkdir(exist_ok=True, parents=True)
    lokiattack_script =  DEOBFUSCATION_TOOLS / "lokiattack" / "run_lokiattack.py"
    cmd = [
        "python3", lokiattack_script.as_posix(),
        "-o", EXPERIMENT_DATA.as_posix(),
        "-j", str(args.max_processes)
    ]
    cmd += list(map(str, MBAS_DIR.glob("*")))
    logger.debug("Running LokiAttack")
    cwd = lokiattack_script.parent
    run_cmd(cmd, cwd)


def run_mba_blast_experiment() -> None:
    if (EXPERIMENT_DATA / "mba_blast_data").exists():
        logger.info(f"{EXPERIMENT_DATA / 'mba_blast_data'} exists -- will not run MBA Blast again")
        return

    # run MBA-Blast
    logger.debug("Installing MBA-Blast dependencies")
    cmd = ["python3", "-m", "pip", "install", "--user", "sympy", "numpy"]
    run_cmd(cmd, Path("."))

    mba_blast_script =  DEOBFUSCATION_TOOLS / "mba_blast" / "run_mba_blast.py"
    cmd = [
        "python3", mba_blast_script.as_posix(),
        "-o", EXPERIMENT_DATA.as_posix()
    ]
    cmd += list(map(str, MBAS_DIR.glob("*")))
    logger.debug("Running MBA-Blast")
    cwd = mba_blast_script.parent
    run_cmd(cmd, cwd)
    logger.debug("Uninstalling MBA-Blast dependencies")
    cmd = ["python3", "-m", "pip", "uninstall", "-y", "sympy", "numpy"]
    run_cmd(cmd, Path("."))


def run_sspam_experiment() -> None:
    if (EXPERIMENT_DATA / "sspam_data").exists():
        logger.info(f"{EXPERIMENT_DATA / 'sspam_data'} exists -- will not run SSPAM again")
        return

    sspam_script =  DEOBFUSCATION_TOOLS / "sspam" / "run_sspam.py"
    sspam_cwd = sspam_script.parent
    # install dependencies
    logger.debug("Installing SSPAM dependencies")
    cmd = [
        "/home/user/.pyenv/versions/3.6.8/bin/python", "-m", "pip", "install", "--user",
        "sympy==0.7.4", "astunparse~=1.3"
    ]
    run_cmd(cmd, sspam_cwd)

    # run SSPAM (with Python 3.6.9 to avoid SSPAM crashing)
    cmd = [
        "/home/user/.pyenv/versions/3.6.8/bin/python", sspam_script.as_posix(),
        "-o", EXPERIMENT_DATA.as_posix()
    ]
    env = os.environ
    env["PYENV_VERSION"] = "3.6.8"
    cmd += list(map(str, MBAS_DIR.glob("*")))
    logger.debug("Running SSPAM")
    run_cmd(cmd, sspam_cwd)

    # uninstall dependencies
    logger.debug("Uninstalling SSPAM dependencies")
    cmd = ["/home/user/.pyenv/versions/3.6.8/bin/python", "-m", "pip", "uninstall", "-y", "sympy", "astunparse"]
    run_cmd(cmd, sspam_cwd, env=env)


def run_experiments(args: Namespace) -> None:
    run_lokiattack_experiment(args)
    run_mba_blast_experiment()
    run_sspam_experiment()


def main(args: Namespace) -> None:
    # Step 1 build binaries
    if args.generate_new_mbas:
        logger.info("Generating MBA formulas")
        create_formulas(args)
    else:
        logger.info(f"Sampling {NUM_FORMULAS} MBA formulas from provided ones")
        sample_formulas(args)
    logger.info("Running experiments")
    run_experiments(args)


if __name__ == "__main__":
    parser = ArgumentParser(description="Run experiment 10 MBA formula deobfuscation")
    parser.add_argument("--mba-formulas", dest="num_formulas", action="store", type=int, default=NUM_FORMULAS,
                        help="Number of obfuscated instances you want to generate (of the same target)")
    parser.add_argument("--log-level", dest="log_level", action="store", type=int, default=1,
                        help="Loglevel (1 = Debug, 2 = Info, 3 = Warning, 4 = Error)")
    parser.add_argument("--max-processes", dest="max_processes", action="store", type=int,
                        default=NUM_CPUS,
                        help="Number of maximal usable processes (defaults to os.cpu_count())")
    parser.add_argument("--generate-new-mbas", action="store_true", default=False,
                        help="Generate new MBA formulas instead of using provided ones (will take some hours/days)")
    cargs = parser.parse_args()

    setup_logging(cargs.log_level * 10)

    main(cargs)
