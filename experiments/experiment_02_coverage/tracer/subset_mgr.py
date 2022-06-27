#!/usr/bin/env python3

"""
Test a subset of obfuscated instances (10) for inputs; uses Intel Pin to trace obfuscated VM
and compares executes handler to the expected execution order defined by bytecode
"""

import json
import logging
import os
import random
import subprocess
from argparse import ArgumentParser, Namespace
from multiprocessing import Pool
from pathlib import Path
from time import time
from typing import Dict, Iterator, List, Tuple, TypeVar

from bytecode_tracer import bytecode_trace


logger = logging.getLogger("SubSetBytecodeVerifier")
PIN_TOOL = Path("./obj-intel64/fn_tracer.so").resolve()
PIN_BINARY = Path("./pin/pin").resolve()

INSTANCE_SUBSET = 10
T = TypeVar("T")

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
        "subset_bytecode_verification.log", "w+"
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


def trace_vm(instance: Path, input_tup: Tuple[List[int], List[int]], id_: int) -> List[int]:
    trace_file = instance / f"pin_vm_trace_{id_}.json"
    stats_file = instance / f"pin_vm_stats_{id_}.txt"
    obf_exe = instance / "obf_exe_patched"
    assert obf_exe.exists(), f"Failed to find obf_exe binary at {obf_exe.as_posix()}"
    env = {}
    for (k, v) in os.environ.items():
        env.update({k : v})
    env.update({
        "FN_STATS_FILE" : stats_file.resolve().as_posix(),
        "FN_TRACE_FILE" : trace_file.resolve().as_posix(),
    })
    cmd = [
        PIN_BINARY.as_posix(), "-t",  PIN_TOOL.as_posix(), "--",
        obf_exe.as_posix()
    ]
    # convert inputs to bytes
    input_1, input_2 = input_tup
    # TODO: temp hack to avoid nullbytes (not passable)
    input_1 = [b if b != 0 else 1 for b in input_1]
    input_2 = [b if b != 0 else 1 for b in input_2]
    input_1_bytes = bytes(input_1)
    input_2_bytes = bytes(input_2)
    cmd.append(input_1_bytes) # type: ignore
    cmd.append(input_2_bytes) # type: ignore
    output = None
    try:
        p = subprocess.run(cmd, shell=False, check=True, env=env,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
        # output = p.stdout.decode("utf-8")
    except subprocess.TimeoutExpired:
        print(f"TIMEOUT: {obf_exe}")
    except subprocess.CalledProcessError as e:
        print(f"ERROR: {obf_exe} -> {e}")
        print(e.stdout.decode("utf-8"))
        print(e.stderr.decode("utf-8"))
    if output:
        print(output)

    with open(trace_file, "r", encoding="utf-8") as f:
        trace: List[int] = json.load(f)
    return trace


def verify_bytecode(task: Tuple[Path, List[Tuple[List[int], List[int]]], int]) -> int:
    """
    1) Parse (expected) bytecode
    2) Trace obf_exe and verify it matches
    """
    instance, inputs, chunk_id = task

    expected_bc_trace = bytecode_trace(instance)
    # TODO: we ignore key currently
    expected_trace = [e.handler_idx for e in expected_bc_trace]

    for input_tup in inputs:
        observed_trace = trace_vm(instance, input_tup, chunk_id)

        if expected_trace != observed_trace:
            logger.error(f"Mismatch for {instance.as_posix()} {inputs}")
            return 1
        # logger.debug("Traces match!")
    return 0


def chunks(lst: List[T], k: int) -> Iterator[List[T]]:
    sz = round(len(lst) / k)
    for i in range(k - 1):
        yield lst[i*sz:(i + 1) * sz]
    yield lst[(k - 1) * sz:]


def main(args: Namespace) -> None:
    """
        1. Identify testcases
        2. For each testcase, locate all instances
        3. For each instance, verify its bytecode is executed correctly
    """
    workdirs = args.path / "workdirs"
    # : Path, inputs_file: Path, allowlist: List[str], subset_size: Optional[int]
    start_time = time()

    assert PIN_TOOL.exists(), f"Failed to find our pintool at {PIN_TOOL.as_posix()}"
    assert PIN_BINARY.exists(), f"Failed to find pin binary at {PIN_BINARY.as_posix()}"

    assert args.inputs_file.exists(), f"Failed to find inputs file at {args.inputs_file.as_posix()}"

    testcases = [tc for tc in workdirs.glob("*")
                    if len(args.allowlist) == 0 or tc.name in args.allowlist]

    with open(args.inputs_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    inputs: List[Tuple[List[int], List[int]]] = [(d["input_1"], d["input_2"]) for d in data]

    if args.num_inputs:
        logger.info(f"Sampling inputs subset of {args.num_inputs} inputs")
        assert args.num_inputs <= len(inputs), \
                f"Input subset of {args.num_inputs} is larger than number of inputs with {len(inputs)}"
        inputs = random.sample(inputs, args.num_inputs)
        assert len(inputs) == args.num_inputs, f"Expected {args.num_inputs} inputs, found {len(inputs)}"

    # we have args.num_jobs cores, which need to process args.subset_size instances
    input_chunks = chunks(inputs, args.num_jobs)

    failed: Dict[str, int] = {}
    for (i, testcase) in enumerate(testcases):
        logger.info(f"Processing {testcase.name}")
        instances: List[Path] = list((testcase / "instances").glob("vm_alu*"))
        logger.info(f"Found {len(instances)} instances")

        # sample subset if specified by user
        if args.subset_size is not None:
            logger.info(f"Sampling instance subset of {args.subset_size} instances")
            assert args.subset_size <= len(instances), \
                    f"Instance subset of {args.subset_size} is larger than set with {len(instances)}"

            instances = random.sample(instances, args.subset_size)
            assert len(instances) == args.subset_size, f"Expected {args.subset_size} instances, found {len(instances)}"

        tasks: List[Tuple[Path, List[Tuple[List[int], List[int]]], int]] = []
        for instance in instances:
            for (i, chunk) in enumerate(input_chunks):
                tasks.append((instance, chunk, i))

        # single-threaded
        # res: List[int] = []
        # for instance in instances:
        #     logger.debug(f"Checking instance {instance.as_posix()}")
        #     res.append(func(instance))
        #     logger.debug("Instance done")
        with Pool() as pool:
            res = pool.map(verify_bytecode, tasks)
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
        description="Verify obf_exe instances execute bytecode"
    )
    parser.add_argument(
        "path", type=Path, help="path to evaluation workdirs directory"
    )
    parser.add_argument(
        "-i", "--inputs-file", dest="inputs_file", type=Path, required=True,
        help="Path to JSON file containing inputs"
    )
    parser.add_argument(
        "--only", dest="allowlist", action="store", nargs="+", default=[],
        help="only run specific tests"
    )
    parser.add_argument(
        "--instance-subset-size", dest="subset_size", type=int, default=None,
        help="How many instances to run (if not set, all are tested)"
    )
    parser.add_argument(
        "--max-processes", dest="num_jobs", type=int, default=os.cpu_count(), help="Number of parallel jobs"
    )
    parser.add_argument("--input-subset-size", dest="num_inputs", type=int, default=None,
        help="Sample a subset of N inputs that are tested (if default=None, all inputs are traced)"
    )

    setup_logging()
    main(parser.parse_args())
