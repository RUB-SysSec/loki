#!/usr/bin/env python3

"""
LokiAttack for MBA formulas
"""

import json
import os
import subprocess
import sys
import time
from argparse import ArgumentParser
from functools import partial
from multiprocessing import Pool
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, Path("../../../../lokiattack/miasm").resolve().as_posix())

from miasm.expression.expression import ExprId
from miasm.expression.simplifications import expr_simp
from miasm.analysis.binary import Container
from miasm.analysis.machine import Machine
from miasm.core.locationdb import LocationDB
from miasm.ir.symbexec import SymbolicExecutionEngine

CLANG_BIN = Path("/llvm/bin/clang").resolve()

TEMPLATE = """
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>


uint64_t target_func(uint64_t x, uint64_t y) {
    return MBA_PLACEHOLDER; 
}

int main(int argc, char* argv[]) {
    if (argc < 3) {
        return 1;
    }
    char *ptr;
    uint64_t x;
    uint64_t y;

    x = strtoul(argv[1], &ptr, 10);
    y = strtoul(argv[2], &ptr, 10);
    
    uint64_t res = target_func(x, y);
    printf("result: 0x%lx\\n", res);

    return 0;
}
"""


def load_mbas(path: Path) -> List[str]:
    assert path.is_file(), f"Path not found or no file: '{path.as_posix()}'"
    with open(path, "r", encoding="utf-8") as f:
        mbas = [l.strip().replace(" ", "") for l in f.readlines() if l.strip()]
    return mbas


def name_to_groundtruth(name: str) -> str:
    if name == "add":
        return "x+y"
    if name == "sub":
        return "x-y"
    if name == "and":
        return "x&y"
    if name == "or":
        return "x|y"
    if name == "xor":
        return "x^y"
    if name == "mul":
        return "x*y"
    if name == "shl":
        return "x<<y"
    raise RuntimeError(f"Unexpected filename '{name}' -- expected one of {{add, sub, xor, or, and, mul, shl}}")


def groundtruth_to_name(groundtruth: str) -> str:
    if groundtruth == "x+y":
        return "add"
    if groundtruth == "x-y":
        return "sub"
    if groundtruth == "x&y":
        return "and"
    if groundtruth == "x|y":
        return "or"
    if groundtruth == "x^y":
        return "xor"
    if groundtruth == "x*y":
        return "mul"
    if groundtruth == "x<<y":
        return "shl"
    raise RuntimeError(f"Unexpected {groundtruth} -- expected one of {{add, sub, xor, or, and, mul, shl}}")


def compile_mba(file_: Path) -> Path:
    file_ = file_.resolve()
    binary: Path = file_.with_suffix("")
    assert file_.exists(), f"C input file not found: '{file_.as_posix()}'"
    # print(f"binary={binary.as_posix()}")
    cmd = [CLANG_BIN.as_posix(), "-O3", file_.as_posix(), "-Wall", "-Werror", "-o", binary.as_posix()]
    # print(f"cmd={' '.join(cmd)}")
    timeout = 30
    subprocess.run(cmd, check=True, cwd=file_.parent.as_posix(), timeout=timeout)
    assert binary.exists()
    return binary


def build_mba(c_file: Path, mba: str) -> Path:
    c_code = TEMPLATE.replace("MBA_PLACEHOLDER", mba)
    with open(c_file, "w", encoding="utf-8") as f:
        f.write(c_code)
    binary = compile_mba(c_file)
    return binary


def get_target_func(binary: Path) -> int:
    cmd = ["nm", binary.as_posix()]
    p = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout = p.stdout.decode()
    for line in stdout.splitlines():
        if "target_func" in line:
            return int(line.split(" ")[0], 16)
    raise RuntimeError(f"Failed to find target_func in stdout: '{stdout}'")


def slice_mba(binary: Path) -> str:
    address = get_target_func(binary)
    loc_db = LocationDB()
    container = Container.from_stream(open(binary, "rb"), loc_db=loc_db)
    machine = Machine(container.arch)
    mdis = machine.dis_engine(container.bin_stream, loc_db=loc_db)
    lifter = machine.ira(mdis.loc_db)
    asm_cfg = mdis.dis_multiblock(address)
    ira_cfg = lifter.new_ircfg_from_asmcfg(asm_cfg)
    assert len(ira_cfg.blocks) == 1, f"Expected exactly 1 IR block (found {len(ira_cfg.blocks)})"
    sb = SymbolicExecutionEngine(lifter)
    next_block = sb.run_block_at(ira_cfg, address)
    assert not next_block.is_cond(), "next_block is cond"
    # sb.dump()
    # return value is stored in RAX
    rax = ExprId("RAX", size=64)
    # RDI = 1. parameter => x, RSI = 2.parameter => y
    ret_val = str(sb.state.symbols[rax])\
                .replace("RDI", "x")\
                .replace("RSI", "y")\
                .replace(" ", "")\
                .replace("+-", "-")
    return ret_val


def test_mba(name: str, groundtruth: str, tup: Tuple[int, str]) -> Tuple[str, str, str, Optional[bool]]:
    idx, mba = tup
    name = f"/tmp/mba_{name}_idx{idx}.c"
    c_file = Path(name)
    exe = Path(name.rstrip(".c"))
    try:
        binary = build_mba(c_file, mba)
        simplified = slice_mba(binary)
    except Exception as e:
        raise RuntimeError(f"mba={mba} raised: {e}") from e
    finally:
        if c_file.exists():
            c_file.unlink()
        if exe.exists():
            exe.unlink()
    return (mba, simplified, groundtruth, check_result(mba, simplified, groundtruth))


def check_result(mba: str, simplified: str, groundtruth: str) -> bool:
    simplified = simplified.strip().replace(" ", "")
    mba = mba.strip().replace(" ", "")
    groundtruth = groundtruth.strip().replace(" ", "")
    if simplified == "None":
        return False
    if simplified == mba:
        return False
    if simplified == groundtruth:
        return True
    if simplified == "(" + groundtruth + ")":
        return True
    return False


def main(paths: List[Path], output_dir: Path, num_jobs: int) -> None:
    stats: Dict[str, Dict[str, Any]] = {"metadata":{}, "data":{}}
    result_dir = (output_dir / "lokiattack_data").resolve()
    result_dir.mkdir()
    starttime = time.time()
    for path in paths:
        print(f"Processing {path}")
        assert "_" in path.name, "Expected filename to be of format OP_depthDEPTH.txt"
        groundtruth = name_to_groundtruth(path.name.split("_", 1)[0])
        mbas = load_mbas(path)
        func = partial(test_mba, path.name, groundtruth)
        with Pool(num_jobs) as pool:
            res = pool.map(func, zip(range(len(mbas)), mbas))
            # DEBUG:
            # res = list(map(func, zip(range(len(mbas)), mbas)))
        with open(result_dir / path.with_suffix(".txt").name, "w", encoding="utf-8") as df:
            for entry in res:
                df.write(",".join(map(str, entry)) + "\n")
        data_result = list(map(lambda t: t[-1], res))
        data = {path.name : {
            "success" : data_result.count(True),
            "failure" : data_result.count(False),
            "error" : data_result.count(None)
        }}
        stats["data"].update(data)
        if len(res):
            success_p = round(100 * data_result.count(True) / len(res), 2)
            failure_p = round(100 * data_result.count(False) / len(res), 2)
            error_p = round(100 * data_result.count(None) / len(res), 2)
        else:
            success_p = 0
            failure_p = 0
            error_p = 0
        print(f"Success: {data_result.count(True)} ({success_p}%)")
        print(f"Failure: {data_result.count(False)} ({failure_p}%)")
        print(f"Error: {data_result.count(None)} ({error_p}%)")
        print(f"Total: {len(res)}")
    runtime = round(time.time() - starttime, 2)
    stats["metadata"]["runtime"] = f"{runtime}s"
    with open(output_dir / "lokiattack_stats.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=4, sort_keys=True)


if __name__ == "__main__":
    parser = ArgumentParser(description="Run LokiAttack on MBA formulas")
    parser.add_argument("paths", nargs="+", type=Path, help="One or more paths to files containing MBAs")
    parser.add_argument("-o", "--output", type=Path, default=Path("."), help="Output file where to store results")
    parser.add_argument("-j", "--max-processes", type=int, default=os.cpu_count(), help="Number of parallel jobs")
    args = parser.parse_args()
    main(args.paths, args.output, args.max_processes)
