#!/usr/bin/python3

"""
Evaluate overhead in terms of runtime.

1. Generate N random inputs
2. Run each testcase (internally run for 10k times) and extract avg runtime
3. Print average value
"""

from argparse import ArgumentParser, Namespace
from functools import partial
from multiprocessing import Manager, Pool
from pathlib import Path
from time import time
from typing import Callable, Dict, List, Optional, Tuple
import logging
import os
import random
import signal
import subprocess
import string

NUM_TESTCASES_TO_GENERATE = 100
TIMEOUT = 60

TIME_BIN: Path = Path("/usr/bin/time")
TIME_ARGS: List[str] = ['--format="OVERHEADtime:%e,max_rss:%M,avg_rss:%t,avg_mem:%K"']
NUM_CPUS: Optional[int] = os.cpu_count()
assert NUM_CPUS is not None, "os.cpu_count() returned None"

logger = logging.getLogger("RuntimeOverhead")


def setup_logging(target_dir: Path) -> None:
    """Setup logger"""
    # Create handlers
    c_handler = logging.StreamHandler()
    f_handler = logging.FileHandler("runtime_overhead.log", "w+")
    fl_handler = logging.FileHandler(target_dir / "runtime_overhead.log", "w+")
    c_handler.setLevel(logging.DEBUG)
    f_handler.setLevel(logging.DEBUG)
    fl_handler.setLevel(logging.DEBUG)
    logger.setLevel(logging.DEBUG)
    c_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    f_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s: %(message)s"))
    fl_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s: %(message)s"))
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)
    logger.addHandler(fl_handler)


### Generate random inputs ###

def identify_pointer_args(src_file: Path) -> List[bool]:
    """Identify which arguments of target_function are pointers"""
    if src_file.name == "input_program.c":
        with open(src_file, "r", encoding="utf-8") as input_program:
            content = [l for l in input_program.readlines() if "long target_function(" in l]
    else:
        with open(src_file, "r", encoding="utf-8") as input_program:
            content = [l for l in input_program.readlines() if 'extern "C"' in l and "target_function(" in l]
    assert len(content) == 1, f"Found {len(content)} definitions of target_function in ./src/input_program.cpp"
    arg_str = content[0].split("target_function(")[1]
    return [bool("*" in arg) for arg in arg_str.split(",")]


def create_random_string_testcase() -> str:
    """
    Create string of random length (16 to 128 chars, both included)
    Strings are prefixed by a capital-letter S. This is conditioned by the obfuscated VM
    interpreting numbers only inputs as number rather than string (and subsequent conversion to long
    rather than passing a pointer) and the fact that small 's' is stripped aways by the obfuscated VM.
    """
    alphabet = string.ascii_letters + string.digits
    length = random.randint(15, 127 + 1)
    return "S" + "".join([random.choice(alphabet) for i in range(length)])


def create_random_testcase() -> str:
    """Create one random testcase"""
    choice: int = random.getrandbits(64) % 5
    if choice == 0:
        return str(random.getrandbits(8))
    if choice == 1:
        return str(random.getrandbits(16))
    if choice == 2:
        return str(random.getrandbits(32))
    if choice == 3:
        return str(random.getrandbits(64))
    if choice == 4:
        special_testcases = [
            0x0, 0x1, 0x2, 0x80, 0xff, 0x8000, 0xffff, 0x8000_0000,
            0xffff_ffff, 0x8000_0000_0000_0000, 0xffff_ffff_ffff_ffff
        ]
        return str(random.choice(special_testcases))
    raise Exception(f"Unexpected case: choice is {choice} but should be 0 to 4 (included)")

### End generate random inputs ###


def test_binary(path: Path, inputs: List[str], timeout: int) -> Tuple[int, Optional[str], Optional[str]]:
    """Run binary with inputs"""
    try:
        cmd: List[str] = [str(path)] + inputs
        process = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout)
        stdout = process.stdout.decode()
        if "Output: " not in stdout or "Time: " not in stdout:
            logger.warning(f"Unexpected output: {stdout} (cmd: {' '.join(cmd)})")
            return (process.returncode, None, None)
        output = stdout.split("Output: ")[1].split("\n")[0].strip()
        runtime = stdout.split("Time: ")[1].split("\n")[0].strip()
        return (process.returncode, output, runtime)
    except subprocess.TimeoutExpired:
        logger.warning(f"Timeout for: {' '.join(cmd)}")
        return (-124, None, None)
    except subprocess.CalledProcessError as err:
        if err.returncode == -signal.SIGFPE:
            #logger.debug(f"SIGFPE for {' '.join(cmd)}")
            pass
        elif err.returncode == -signal.SIGSEGV:
            #logger.debug(f"SIGSEGV for {' '.join(cmd)}")
            pass
        else:
            logger.warning(f"Process errored out with {err} for \"{' '.join(cmd)}\"")
        return (err.returncode, None, None)
    return (1, None, None)


def enumerate_testcases(workdirs: Path, allowlist: List[str], denylist: List[str]) -> List[Path]:
    """
    Enumerate all testcases included in allowlist.
    If no allowlist entry exists, enumerate all entries not on denylist
    """
    testcases = []
    if allowlist:
        testcases = [testcase for testcase in workdirs.glob("*") if testcase.name in allowlist]
    else:
        testcases = [testcase for testcase in workdirs.glob("*") if testcase.name not in denylist]
    logger.info(f"Found {len(testcases)} testcases")
    return testcases


def get_input_tuples(testcase: Path, num_random_inputs: int) -> List[List[str]]:
    """Return random input tuples tailored to current testcase"""
    if (testcase / "src" / "input_program.cpp").exists():
        arg_to_str = identify_pointer_args(testcase / "src" / "input_program.cpp")
    else:
        arg_to_str = identify_pointer_args(testcase / "src" / "input_program.c")
    input_arrays = [[create_random_string_testcase() for i in range(num_random_inputs)] \
        if arg else \
        [create_random_testcase() for i in range(num_random_inputs)] for arg in arg_to_str]
    return list(map(list, zip(*input_arrays)))


def update_stat_count(stats: Dict[str, List[str]], key: str) -> None:
    """Update stats count by 1"""
    err_stats = stats[key]
    if not err_stats:
        stats[key] = ["1"]
    else:
        err_stats[0] = str(int(err_stats[0]) + 1)


def run_binary(stats: Dict[str, List[str]], binary: Path, input_tuple: List[str], timeout: int) -> None:
    """Execute a given binary + input_tuple and note populate stats data structure with results"""
    ret_code, output, time_str = test_binary(binary, input_tuple, timeout=timeout)
    if ret_code != 0 or output is None or time_str is None:
        if ret_code == -signal.SIGFPE:
            update_stat_count(stats, "SIGFPE")
        elif ret_code == -signal.SIGSEGV:
            update_stat_count(stats, "SIGSEGV")
        elif ret_code == -124:
            update_stat_count(stats, "Timeout")
        else:
            update_stat_count(stats, "other")
        return
    stats["time"].append(time_str.rstrip("ms"))
    stats["output"].append(output)


def collect_tuples(stats: Dict[str, List[str]], binary: Path, input_tuples: List[List[str]], timeout: int) \
    -> List[Callable[..., None]]:
    """Collect executable functions for each input tuple"""
    tasks: List[Callable[..., None]] = []
    for tup in input_tuples:
        tasks.append(partial(run_binary, stats, binary, tup, timeout))
    return tasks


def collect_instances(stats: Dict[str, Dict[str, List[str]]], testcase_dir: Path,
            input_tuples: List[List[str]], timeout: int) -> List[Callable[..., None]]:
    """Collect executable functions for each instance and the original binary"""
    tasks: List[Callable[..., None]] = []
    orig_exe = testcase_dir / "bin" / "orig_exe"
    tasks.extend(collect_tuples(stats["orig"], orig_exe, input_tuples, timeout))
    instances = list((testcase_dir / "instances").glob("vm_alu*"))
    # check if we have tigress instances - TODO: improve
    if len(instances) == 0:
        instances = list((testcase_dir / "instances").glob("tigress*"))
    logger.info(f"Found {len(instances)} instances")
    for instance in instances:
        obf_exe = (instance / "obf_exe")
        tasks.extend(collect_tuples(stats["obf"], obf_exe, input_tuples, timeout))
    return tasks


def _stub(func: Callable[..., None]) -> None:
    """Stub which calls first parameter"""
    func()


def _unpack_val_from_list(val_list: List[str], name: str) -> int:
    """Unpack value"""
    vals = [int(val) for val in val_list]
    assert len(vals) == 1, f"{name}: Mulitple values: {val_list}"
    return vals[0]


def extract_statistics(data: Dict[str, Dict[str, Dict[str, List[str]]]], name: str, args: Namespace) -> str: # pylint: disable = redefined-outer-name
    """Convert statistics into printable string"""
    data_str = f"Statistics for {name}:\n"
    for tname in sorted(data):
        v_dd = data[tname]
        data_str += f"{tname}:\n"
        avgs: List[float] = []
        for (obf_type, v_d) in sorted(v_dd.items()):
            data_str += f"\t- {obf_type}"

            time_list = [float(val) for val in v_d["time"]]
            if time_list:
                avg = sum(time_list) / len(time_list)
                avgs.append(avg)
                data_str += f" - avg time: {round(avg, 4)} microseconds\n"

            for (err_name, err_list) in v_d.items():
                if err_name == "time" or err_name == "output":
                    continue
                num_errs = _unpack_val_from_list(err_list, err_name)
                if num_errs:
                    data_str += f"\t\t- #{err_name}s: {num_errs}\n"
        obf = v_dd["obf"]
        orig = v_dd["orig"]

        output_obf = set(obf["output"])
        output_orig = set(orig["output"])
        if output_obf != output_orig:
            logger.warning(f"{tname}: output mismatch - set difference {output_obf.difference(output_orig)}")

        times_obf = [float(val) for val in obf["time"]]
        times_orig = [float(val) for val in orig["time"]]
        if times_obf and times_orig:
            avg_obf = sum(times_obf) / len(times_obf)
            avg_orig = sum(times_orig) / len(times_orig)
            data_str += f"\t- Factor: {int(round(avg_obf / avg_orig, 0))}\n"
    return data_str


def main(workdirs: Path, args: Namespace) -> None: # pylint: disable = redefined-outer-name
    """
        1. Sample testcases in eval_dir; Collect each instance and orig_exe
        2. For each sampled executable, extract time
    """
    start_time = time()

    testcases = enumerate_testcases(workdirs, args.allow, args.deny)

    tasks: List[Callable[..., None]] = []
    mgr = Manager()
    #{TESTCASE_NAME : (ORIG{time : [time / input_pair], time_orig : [time / input_pair]})]
    data: Dict[str, Dict[str, Dict[str, List[str]]]] = mgr.dict()
    prev_len = len(tasks)
    for (i, testcase) in enumerate(testcases):
        data[testcase.name] = mgr.dict({
            "orig":mgr.dict(
                {"time":mgr.list(), "output":mgr.list(), "SIGFPE":["0"],
                "SIGSEGV":["0"], "Timeout":["0"], "other":["0"]}
            ),
            "obf":mgr.dict(
                {"time":mgr.list(), "output":mgr.list(), "SIGFPE":["0"],
                "SIGSEGV":["0"], "Timeout":["0"], "other":["0"]}
            )
        })
        input_tuples: List[List[str]] = get_input_tuples(testcase, args.num_random_inputs)
        logger.info(f"Collecting {testcase.name} ({i+1}/{len(testcases)})")
        tasks.extend(collect_instances(data[testcase.name], testcase, input_tuples, args.timeout))
        logger.info(f"Added {len(tasks) - prev_len} new tasks")
        prev_len = len(tasks)
    logger.info(f"Collected {len(tasks)} tasks in total")

    logger.info("Randomizing order of tasks")
    # randomize order of tasks
    random.shuffle(tasks)

    logger.info(f"Executing tasks in up to {args.num_jobs} processes. This may take some while..")
    # execute tasks in random order
    with Pool(args.num_jobs) as pool:
        # we can't use a lambda as python cannot pickle it without additional import: (lambda f: f())
        pool.map(_stub, tasks)

    data_str = extract_statistics(data, workdirs.parent.name, args)
    logger.info(data_str)


    logger.info(f"Completed {len(testcases)} testcases in {time() - start_time:0.2f}s")


if __name__ == "__main__":
    parser = ArgumentParser(description="Evaluate overhead in terms of runtime")
    parser.add_argument("path", type=Path, help="path to evaluation workdirs directory")
    parser.add_argument("--allow", action="store", nargs="+", default=[], help="only run specified tests")
    parser.add_argument("--deny", action="store", nargs="+", default=[],
                        help="avoid running specified tests (ignored if allowlist is specified)")
    parser.add_argument("-n", "--num-random-inputs", type=int, default=NUM_TESTCASES_TO_GENERATE,
                        help="number of random inputs that should be run for overhead measurements")
    parser.add_argument("--timeout", dest="timeout", type=int, default=TIMEOUT,
                        help="timeout for running each binary")
    parser.add_argument("--max-processes", dest="num_jobs", type=int, default=NUM_CPUS,
                        help="Number of maximal usable processes (defaults to os.cpu_count())")
    args = parser.parse_args()

    target_path = args.path.resolve()
    setup_logging(target_path)
    main(target_path / "workdirs", args)
