#!/usr/bin/env python3

"""
Run SSPAM on MBA formulas -- requires Python version older than 3.8
"""

import json
import multiprocessing
import time
from argparse import ArgumentParser
from functools import partial
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from sspam import simplifier


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


def test_mba(groundtruth: str, mba: str) -> Tuple[str, Optional[bool]]:
    try:
        simplified = simplifier.simplify(mba) # type: ignore
    except Exception as e:
        if str(e).strip() == "exec() arg 1 must be a string, bytes or code object":
            return ("None", None)
        if str(e).strip() == "maximum recursion depth exceeded":
            return ("None", None)
        if str(e).strip() == "maximum recursion depth exceeded while calling a Python object":
            return ("None", None)
        raise RuntimeError(f"mba={mba} raised: {e}") from e
    return (simplified, check_result(mba, simplified, groundtruth))


def check_result(mba: str, simplified: str, groundtruth: str) -> Optional[bool]:
    simplified = simplified.strip().replace(" ", "")
    mba = mba.strip().replace(" ", "")
    groundtruth = groundtruth.strip().replace(" ", "")
    if simplified == "None":
        return False
    if simplified == mba:
        return False
    if simplified == "(" + groundtruth + ")":
        return True
    if simplified == groundtruth:
        return True
    return False


def main(paths: List[Path], output_dir: Path) -> None:
    stats: Dict[str, Dict[str, Any]] = {"metadata":{}, "data":{}}
    result_dir = (output_dir / "sspam_data").resolve()
    result_dir.mkdir()
    starttime = time.time()
    for path in paths:
        print(f"Processing {path}")
        assert "_" in path.name, "Expected filename to be of format OP_depthDEPTH.txt"
        groundtruth = name_to_groundtruth(path.name.split("_", 1)[0])
        mbas = load_mbas(path)
        func = partial(test_mba, groundtruth)
        with multiprocessing.Pool() as pool:
            res: List[Tuple[str, str, str, Optional[bool]]] = []
            multiple_results = [(mbas[i], pool.apply_async(func, (mbas[i],))) for i in range(len(mbas))]
            for (mba_in, res_in) in multiple_results:
                simplified = "None"
                success: Optional[bool] = None
                try:
                    simplified, success = res_in.get(timeout=600)
                except multiprocessing.TimeoutError:
                    pass
                finally:
                    res.append((mba_in, simplified, groundtruth, success))
        with open(result_dir / path.with_suffix(".txt").name, "w", encoding="utf-8") as df:
            for entry in res:
                df.write(",".join(map(str, entry)) + "\n")
        data_result = list(map(lambda t: t[-1], res))
        data = {path.name : {
                    "success" : data_result.count(True),
                    "failure" : data_result.count(False),
                    "error"   : data_result.count(None)
        }}
        with open(result_dir / path.with_suffix(".json").name, "w", encoding="utf-8") as df:
            json.dump(data, df)
        stats["data"].update(data)
        if len(res) > 0:
            success_p = round(100 * data_result.count(True) / len(res), 2)
            failure_p = round(100 * data_result.count(False) / len(res), 2)
            error_p   = round(100 * data_result.count(None) / len(res), 2)
        else:
            success_p = 0
            failure_p = 0
            error_p   = 0
        print(f"Success: {data_result.count(True)} ({success_p}%)")
        print(f"Failure: {data_result.count(False)} ({failure_p}%)")
        print(f"Error: {data_result.count(None)} ({error_p}%)")
        print(f"Total: {len(res)}")
    runtime = round(time.time() - starttime, 2)
    stats["metadata"]["runtime"] = f"{runtime}s"
    with open(output_dir / "sspam_stats.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=4, sort_keys=True)


if __name__ == "__main__":
    parser = ArgumentParser(description="Run SSPAM on MBA formulas (requires Python 3.6.8 or older)")
    parser.add_argument("paths", nargs="+", type=Path, help="One or more paths to files containing MBAs")
    parser.add_argument("-o", "--output", type=Path, default=Path("."), help="Output file where to store results")
    args = parser.parse_args()
    main(args.paths, args.output)
