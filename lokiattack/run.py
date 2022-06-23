#!/usr/bin/python3

"""
Run LokiAttack with a specified plugin on specified workdir
"""

import functools
import logging
import os
import subprocess
from argparse import ArgumentParser, Namespace
from enum import Enum
from multiprocessing import Pool
from pathlib import Path
from time import time
from typing import List, Optional, Tuple

OBF_EXE_NAME = "obf_exe"
TESTCASE_REPO = Path("../loki/testcases").resolve()
TIMEOUT = 3600

NUM_CPUS: Optional[int] = os.cpu_count()
assert NUM_CPUS is not None, "os.cpu_count() returned None"

logger = logging.getLogger("LokiAttack")

class Plugins(Enum):
    """
    Available plugins
    """
    SMT = 0
    TAINT_BIT = 1
    TAINT_BYTE = 2
    BACKWARD_SLICING = 3
    SYMBOLIC_EXECUTION = 4
    SYMBOLIC_EXECUTION_DEPTH_5 = 5
    MBA_DUMPER = 6
    SYNTHESIS = 7
    COMPILER_OPTIMIZATIONS = 8

    @staticmethod
    def from_name(name: str) -> "Plugins":
        name = name.lower().strip()
        if name in ("smt", "key_encodings"):
            return Plugins.SMT
        if name in ("se", "symex", "symbolic_execution"):
            return Plugins.SYMBOLIC_EXECUTION
        if name in ("se_depth_5", "symex_depth_5", "symbolic_execution_depth_5"):
            return Plugins.SYMBOLIC_EXECUTION_DEPTH_5
        if name in ("tm", "taint_miasm", "taint_bit"):
            return Plugins.TAINT_BIT
        if name in ("tt", "taint_triton", "taint_byte"):
            return Plugins.TAINT_BYTE
        if name in ("slice", "slicing", "backward_slicing"):
            return Plugins.BACKWARD_SLICING
        if name in ("dump_mba", "mba_dump", "mba_dumper"):
            return Plugins.MBA_DUMPER
        if name in ("synthesis", "syntia"):
            return Plugins.SYNTHESIS
        if name in ("dce", "deadcode_elimination", "dead_code_elimination", "compiler_optimizations"):
            return Plugins.COMPILER_OPTIMIZATIONS
        raise NotImplementedError(f"Unsupported plugin name: {name}")


def setup_logging(target_dir: Path, plugin: str, log_level: int = logging.DEBUG) -> None:
    """Setup logger"""
    # Create handlers
    c_handler = logging.StreamHandler()
    f_handler = logging.FileHandler("lokiattack.log", "w+")
    fl_handler = logging.FileHandler(target_dir.resolve() / f"lokiattack_{plugin}.log", "w+")
    c_handler.setLevel(log_level)
    f_handler.setLevel(log_level)
    fl_handler.setLevel(logging.DEBUG)
    logger.setLevel(logging.DEBUG)
    c_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    f_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s: %(message)s"))
    fl_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s: %(message)s"))
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)
    logger.addHandler(fl_handler)


def enumerate_testcases(allowlist: List[str], denylist: List[str]) -> List[Path]:
    """
    Enumerate all testcases included in allowlist.
    If no allowlisted entry exists, enumerate all entries not on denylist
    """
    testcases = []
    if allowlist:
        testcases = [
            Path(testcase) for testcase in TESTCASE_REPO.glob("**/*.c*") if testcase.name.split(".c")[0] in allowlist
        ]
    else:
        testcases = [
            Path(testcase) for testcase in TESTCASE_REPO.glob("**/*.c*") if testcase.name.split(".c")[0] not in denylist
        ]
    logger.info(f"Found {len(testcases)} testcases")
    return testcases


def get_target_instances(path: Path, allowlist: List[str], denylist: List[str]) -> List[Path]:
    if allowlist or denylist:
        logger.debug("Selecting only subset of instances")
        target_instances = []
        testcases = enumerate_testcases(allowlist, denylist)
        for tc in testcases:
            testcase_path = path / "workdir" / tc.name
            target_instances.extend(list(testcase_path.glob(f"**/{OBF_EXE_NAME}")))
        return target_instances
    else:
        return list(path.glob(f"**/{OBF_EXE_NAME}"))


def test_smt_instance(cmd: List[str], target: Path) -> Optional[str]:
    cmd += [target.parent.as_posix()]
    try:
        p = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        logger.error(e)
        if e.output:
            logger.warning(e.output.decode())
        return None
    except subprocess.TimeoutExpired as e:
        logger.error(e)
        return None
    output = p.stdout.decode().strip()
    if output:
        print(output)
        return output
    else:
        logger.warning(f"No output for {target.as_posix()}")
        return None


def run_smt_plugin(cmd: List[str], num_jobs: int, target_instances: List[Path]) \
            -> List[Optional[str]]:
    with Pool(num_jobs) as pool:
        fn = functools.partial(test_smt_instance, cmd)
        results = pool.map(fn, target_instances)
    assert len(results) == len(target_instances)
    return results


def test_instance(cmd: List[str], attacker_type: str, target_tuple: Tuple[Path, int]) -> Optional[str]:
    target, core_semantics_idx = target_tuple
    cmd += [target.parent.as_posix()]
    cmd += [str(core_semantics_idx)]
    cmd += [attacker_type]
    print(cmd)
    try:
        p = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        logger.error(e)
        if e.output:
            logger.warning(e.output.decode())
        return None
    except subprocess.TimeoutExpired as e:
        logger.error(e)
        return None
    output = p.stdout.decode().strip()
    if output:
        print(output)
        return output
    else:
        logger.warning(f"No output for {target.as_posix()}")
        return None


def run_syntactic_simplification_plugin(cmd: List[str], num_jobs: int, attacker_type: str, \
            target_instances: List[Path]) -> List[Optional[str]]:
    logger.debug(f"Command is {' '.join(cmd)} INSTANCE_PATH")
    targets = []
    for i in range(7):
        for obf_exe in target_instances:
            targets.append((obf_exe, i))
    with Pool(num_jobs) as pool:
        fn = functools.partial(test_instance, cmd, attacker_type)
        results = pool.map(fn, targets)
    assert len(results) == len(targets)
    return results


def test_handlerlist_instance(cmd: List[str], target: Tuple[str, str, str]) -> Optional[str]:
    cmd += [e for e in target]
    try:
        p = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        logger.error(e)
        if e.output:
            logger.warning(e.output.decode())
        return None
    except subprocess.TimeoutExpired as e:
        logger.error(e)
        return None
    output = p.stdout.decode().strip()
    if output:
        print(output)
        return output
    else:
        logger.warning(f"No output for {target[0]}")
        return None


def run_handlerlist_plugin(cmd: List[str], num_jobs: int, handler_list_file: Path, expected_elems_per_line: int) \
            -> List[Optional[str]]:
    logger.debug(f"Command is {' '.join(cmd)} INSTANCE_PATH")
    with open(handler_list_file, "r", encoding="utf-8") as f:
        content = [l.strip() for l in f.readlines() if l.strip()]
    assert len(content) > 0, "Expected at least one line in file"
    elems_per_line = len(content[0].strip().split())
    assert elems_per_line  == expected_elems_per_line, \
            f"Found {elems_per_line} elements in handler_list[0], expected {expected_elems_per_line}"
    data = [tuple(l.split(" ")) for l in content]
    with Pool(num_jobs) as pool:
        fn = functools.partial(test_handlerlist_instance, cmd)
        results = pool.map(fn, data)
    assert len(results) == len(data)
    return results


def run_plugin(plugin_name: str, num_jobs: int, attacker_type: str, target_instances: List[Path], \
            handler_list_file: Optional[Path]) -> List[Optional[str]]:
    """
    For legacy reasons, this executes the plugin in a subprocess.
    """
    plugin = Plugins.from_name(plugin_name)
    logger.info(f"Using plugin {plugin.name} -- num_jobs={num_jobs}, attacker_type={attacker_type}")

    cmd = ["python3"]
    if plugin == Plugins.SMT:
        assert attacker_type == "static", "SMT experiments always assume static attacker"
        cmd += ["plugin_smt.py"]
        # note: this is a special case; this plugin does not expect a core semantics index
        return run_smt_plugin(cmd, num_jobs, target_instances)
    if plugin == Plugins.TAINT_BYTE:
        cmd += ["plugin_taint_triton.py"]
        return run_syntactic_simplification_plugin(cmd, num_jobs, attacker_type, target_instances)
    if plugin == Plugins.TAINT_BIT:
        cmd += ["plugin_taint_miasm.py"]
        return run_syntactic_simplification_plugin(cmd, num_jobs, attacker_type, target_instances)
    if plugin == Plugins.BACKWARD_SLICING:
        cmd += ["plugin_backward_slicing.py"]
        return run_syntactic_simplification_plugin(cmd, num_jobs, attacker_type, target_instances)
    if plugin == Plugins.SYMBOLIC_EXECUTION:
        cmd += ["plugin_symbolic_execution.py"]
        return run_syntactic_simplification_plugin(cmd, num_jobs, attacker_type, target_instances)
    if plugin == Plugins.SYMBOLIC_EXECUTION_DEPTH_5:
        cmd += ["plugin_symbolic_execution_depth_5.py"]
        return run_syntactic_simplification_plugin(cmd, num_jobs, attacker_type, target_instances)
    if plugin == Plugins.MBA_DUMPER:
        assert attacker_type == "dynamic", "MBA diversity was only tested for stronger dynamic attacker"
        cmd += ["plugin_mba_dumper.py"]
        return run_syntactic_simplification_plugin(cmd, num_jobs, attacker_type, target_instances)
    if plugin == Plugins.SYNTHESIS:
        assert attacker_type == "dynamic", "Synthesis was only tested for stronger dynamic attacker"
        if not handler_list_file:
            logger.error("Synthesis plugin requires a path to a file containing a list of PATH HANDLER_IDX VALID_KEY")
            assert handler_list_file, \
                    "Synthesis plugin requires a path to a file containing a list of PATH HANDLER_IDX VALID_KEY"
        cmd += ["plugin_synthesis.py"]
        return run_handlerlist_plugin(cmd, num_jobs, handler_list_file, 3)
    if plugin == Plugins.COMPILER_OPTIMIZATIONS:
        assert attacker_type == "static", "Compiler optimizations assume static attacker"
        if not handler_list_file:
            logger.error(
                "Compiler optimizations plugin requires a path to a file containing a list of PATH HANDLER_ADDRESS"
            )
            assert handler_list_file, \
                    "Compiler optimizations plugin requires a path to a file containing a list of PATH HANDLER_ADDRESS"
        cmd += ["plugin_compiler_optimizations.py"]
        return run_handlerlist_plugin(cmd, num_jobs, handler_list_file, 2)
    else:
        raise NotImplementedError(f"{plugin} not supported yet")


def main(args: Namespace) -> None:
    start = time()
    target_instances = get_target_instances(args.path, args.allow, args.deny)
    logger.info(f"Found {len(target_instances)} obfuscated instances")

    attacker_type = args.attacker_type.lower()
    if attacker_type not in ("static", "dynamic"):
        raise RuntimeError(f"Unknown attacker type '{attacker_type}' -- must be 'static' or 'dynamic'")

    output = run_plugin(args.plugin_name, args.max_processes, attacker_type, target_instances, args.handler_list)
    if args.output:
        logger.debug(f"Writing output to {args.output.as_posix()}")
        with open(args.output, "w", encoding="utf-8") as f:
            f.write("\n".join(map(str, output)))
    logger.info(f"Done in {time() - start:.2f}s")


if __name__ == "__main__":
    parser = ArgumentParser(description="LokiAttack manager script")
    parser.add_argument("plugin_name", help="Name of LokiAttack plugin")
    parser.add_argument("path", type=Path, help="path to evaluation directory")
    parser.add_argument("attacker_type", help="Whether attacker is static or dynamic")
    parser.add_argument("-o", "--output", type=Path, help="Output file where to store results")
    parser.add_argument("--allow", action="store", nargs="+", default=[], help="only run these tests")
    parser.add_argument("--deny", action="store", nargs="+", default=[],
                        help="avoid running these tests (ignored if allowlist is specified)")
    parser.add_argument("--instances", dest="num_instances", action="store", type=int, default=None,
                        help="Number of obfuscated instances you expect (assertion)")
    parser.add_argument("--debug", dest="debug", action="store_true", default=False,
                        help="Do not delete build artifacts (increased disk usage)")
    parser.add_argument("--log-level", dest="log_level", action="store", type=int, default=1,
                        help="Loglevel (1 = Debug, 2 = Info, 3 = Warning, 4 = Error)")
    parser.add_argument("--verification-rounds", dest="verification_iterations", action="store", type=int, default=1000,
                        help="Number of verification iterations to run")
    parser.add_argument("--handler-list", type=Path, default=None,
                        help="Path to list of handlers (ONLY REQUIRED FOR SYNTHESIS OR DEAD CODE ELIMINATION)")
    parser.add_argument("--max-processes", dest="max_processes", action="store", type=int,
                        default=NUM_CPUS,
                        help="Number of maximal usable processes (defaults to os.cpu_count())")
    cargs = parser.parse_args()

    setup_logging(cargs.path, cargs.plugin_name, cargs.log_level * 10)

    main(cargs)
