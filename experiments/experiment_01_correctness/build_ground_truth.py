#!/usr/bin/env python3

"""
Build ground truth using inputs.json file
"""

from argparse import ArgumentParser
from pathlib import Path
from time import time
from typing import List, Optional
import logging
import os
import subprocess

logger = logging.getLogger("GroundTruther")
ORACLE_LIB = Path("./target/debug/libcorrectness_oracle.so").resolve()

TESTCASES = [
    "aes_encrypt",
    "des_encrypt",
    "md5",
    "rc4",
    "sha1"
]

def setup_logging() -> None:
    """Setup logger"""
    # Create handlers
    c_handler = logging.StreamHandler()  # pylint: disable=invalid-name
    f_handler = logging.FileHandler(
        "ground_truth.log", "w+"
    )  # pylint: disable=invalid-name
    c_handler.setLevel(logging.DEBUG)
    f_handler.setLevel(logging.DEBUG)
    logger.setLevel(logging.DEBUG)
    c_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    f_handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
    )
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)


def get_symbol(binary: Path) -> Optional[int]:
    cmd = ["nm", binary.as_posix()]
    output = None
    try:
        p = subprocess.run(cmd, shell=False, check=True, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
        output = p.stdout.decode("utf-8")
    except subprocess.TimeoutExpired:
        print(f"TIMEOUT: nm {binary.as_posix()}")
        return None
    except subprocess.CalledProcessError as e:
        print(f"ERROR: {' '.join(cmd)} -> {str(e)}")
        print(e.stdout.decode("utf-8"))
        print(e.stderr.decode("utf-8"))
        return None
    if not output:
        print(f"ERROR: No output by nm {binary.as_posix()}")
        return None
    target_function = None
    for l in [l.strip() for l in output.splitlines() if l.strip()]:
        if "T target_function" in l:
            target_function = int(l.split(" ", 1)[0], 16)
    if target_function is None:
        print(f"ERROR: Failed to locate target_function via nm {binary.as_posix()}")
        return None
    return target_function


def run_oracle(testcase: Path, inputs_file: Path) -> None:
    """
    LD_PRELOAD=$PWD/target/debug/libcorrectness_oracle.so <path_to_target>/instances/bin/orig_exe
    """
    orig_exe = testcase / "bin" / "orig_exe"
    assert orig_exe.exists(), f"Failed to find orig_exe binary at {orig_exe.as_posix()}"
    output_file = testcase / f"inputs_{testcase.name}.json"

    # get symbols from binary
    target_function = get_symbol(orig_exe)
    assert target_function is not None, f"Failed to retrieve symbols for {orig_exe.as_posix()}"

    env = {}
    for (k, v) in os.environ.items():
        env.update({k : v})
    env.update({
        "LD_PRELOAD" : ORACLE_LIB.as_posix(),
        "ORACLE_TC_NAME" : testcase.name,
        "ORACLE_INPUTS_FILE" : inputs_file.resolve().as_posix(),
        "ORACLE_OUTPUT_FILE" : output_file.resolve().as_posix(),
        "ORACLE_ADDRESS_TARGET_FUNCTION" : str(target_function),
    })

    cmd = [orig_exe.as_posix(), "A", "A"]
    output = None
    try:
        p = subprocess.run(cmd, shell=False, check=True, env=env,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
        output = p.stdout.decode("utf-8")
    except subprocess.TimeoutExpired:
        print(f"TIMEOUT: {orig_exe}")
    except subprocess.CalledProcessError as e:
        print(f"ERROR: {orig_exe} -> {e}")
        print(e.stdout.decode("utf-8"))
        print(e.stderr.decode("utf-8"))
    if output:
        print(output)

def main(workdirs: Path, inputs_file: Path, allowlist: List[str]) -> None:
    """
        1. Identify testcases
        2. Build groundtruth using ground truth oracle
    """
    start_time = time()

    assert ORACLE_LIB.exists(), f"Failed to find oracle lib at {ORACLE_LIB.as_posix()}"

    testcases = [tc for tc in workdirs.glob("*")
                    if len(allowlist) == 0 or tc.name in allowlist]


    for testcase in testcases:
        logger.info(f"Processing {testcase.name}")
        run_oracle(testcase, inputs_file)
    logger.info(
        f"Completed {len(testcases)} testcases in {time() - start_time:0.2f}s"
    )


if __name__ == "__main__":
    parser = ArgumentParser(
        description="Build ground truth for correctness tests"
    )
    parser.add_argument(
        "path", nargs=1, help="path to evaluation workdirs directory"
    )
    parser.add_argument(
        "-i", "--inputs-file", dest="inputs_file", type=Path, required=True,
        help="Path to JSON file containing inputs"
    )
    parser.add_argument(
        "--only", dest="allowlist", action="store", nargs="+", default=[],
        help="only run specific tests"
    )
    args = parser.parse_args() # pylint: disable=invalid-name

    target_path = Path(args.path[0]).resolve() # pylint: disable = invalid-name
    setup_logging()
    main(target_path / "workdirs", args.inputs_file, args.allowlist)
