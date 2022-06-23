#!/usr/bin/env python3

"""
Check correctness
"""

import logging
import os
import subprocess
from argparse import ArgumentParser
from functools import partial
from multiprocessing import Pool
from pathlib import Path
from time import time
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger("Checker")
CHECKER_LIB = Path("./target/debug/libcorrectness_checker_runtime.so").resolve()

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
        "checker.log", "w+"
    )  # pylint: disable=invalid-name
    c_handler.setLevel(logging.DEBUG)
    f_handler.setLevel(logging.DEBUG)
    logger.setLevel(logging.INFO)
    c_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    f_handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
    )
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)


def get_symbols(binary: Path) -> Optional[Tuple[int, int]]:
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
    context = None
    vm_setup = None
    for l in [l.strip() for l in output.splitlines() if l.strip()]:
        if "B context" in l:
            context = int(l.split(" ", 1)[0], 16)
        elif "T _Z8vm_setupPmR7Contextm" in l:
            vm_setup = int(l.split(" ", 1)[0], 16)
    if context is None:
        print(f"ERROR: Failed to locate context via nm {binary.as_posix()}")
        return None
    if vm_setup is None:
        print(f"ERROR: Failed to locate context via nm {binary.as_posix()}")
        return None
    return (context, vm_setup)


def run_checker(tc_name: str, inputs_file: Path, instance: Path) -> bool:
    """
    LD_PRELOAD=$PWD/target/debug/libcorrectness_checker_runtime.so <path_to_target>/instances/vm_alu<NUMBER>/obf_exe
    """
    obf_exe = instance / "obf_exe"
    assert obf_exe.exists(), f"Failed to find obf_exe binary at {obf_exe.as_posix()}"

    # get symbols from binary
    logger.debug("Using nm to parse symbols")
    tup = get_symbols(obf_exe)
    assert tup is not None, f"Failed to retrieve symbols for {obf_exe.as_posix()}"
    addr_context, addr_vm_setup = tup

    env = {}
    for (k, v) in os.environ.items():
        env.update({k : v})
    env.update({
        "LD_PRELOAD" : CHECKER_LIB.as_posix(),
        "CHECKER_TC_NAME" : tc_name,
        "CHECKER_INPUTS_FILE" : inputs_file.resolve().as_posix(),
        "CHECKER_ADDRESS_CONTEXT" : str(addr_context),
        "CHECKER_ADDRESS_VM_SETUP" : str(addr_vm_setup),
    })

    cmd = [obf_exe.as_posix(), "A", "A"]
    output = None
    failed = False
    logger.debug("Launching checker now..")
    try:
        p = subprocess.run(cmd, shell=False, check=True, env=env,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
        output = p.stdout.decode("utf-8")
    except subprocess.TimeoutExpired:
        logger.error(f"TIMEOUT: {obf_exe}")
        failed = True
    except subprocess.CalledProcessError as e:
        logger.error(f"ERROR: {obf_exe} -> {e}")
        logger.error(e.stdout.decode("utf-8"))
        logger.error(e.stderr.decode("utf-8"))
        failed = True
    if output:
        print(output)
        if "ERROR" in output:
            logger.error(obf_exe.as_posix() + ": " + output)
            failed = True
    else:
        failed = True
    return failed


def main(workdirs: Path, inputs_file: Path, allowlist: List[str]) -> None:
    """
        1. Identify testcases
        2. Run checker for each instance
    """
    start_time = time()

    assert CHECKER_LIB.exists(), f"Failed to find oracle lib at {CHECKER_LIB.as_posix()}"

    testcases = [tc for tc in workdirs.glob("*")
                    if len(allowlist) == 0 or tc.name in allowlist]

    failed: Dict[str, int] = {}
    for testcase in testcases:
        logger.info(f"Processing {testcase.name}")
        instances = (testcase / "instances").glob("vm_alu*")
        inputs_file = testcase / f"inputs_{testcase.name}.json"
        assert inputs_file.exists(), f"Failed to find inputs_{testcase.name}.json file (produced by oracle)"
        func = partial(run_checker, testcase.name, inputs_file)
        with Pool() as pool:
            res = pool.map(func, instances)
        num_failed_instances = sum(res)
        logger.info(f"{testcase.name}: {num_failed_instances} instances failed")
        failed[testcase.name] = num_failed_instances

    runtime = time() - start_time
    res_str = "failing instances: "
    for k, v in failed.items():
        res_str += f"{k}: {v} / 1000; "
    res_str = res_str[:-2]
    logger.info(
        f"Completed {len(testcases)} testcases in {runtime:0.2f}s -- {res_str}"
    )


if __name__ == "__main__":
    parser = ArgumentParser(
        description="Build ground truth for correctness tests"
    )
    parser.add_argument(
        "path", nargs=1, help="path to evaluation workdirs directory"
    )
    parser.add_argument(
        "--only", dest="allowlist", action="store", nargs="+", default=[],
        help="only run specific tests"
    )
    args = parser.parse_args() # pylint: disable=invalid-name

    target_path = Path(args.path[0]).resolve() # pylint: disable = invalid-name
    setup_logging()
    main(target_path / "workdirs", Path("inputs.json"), args.allowlist)
