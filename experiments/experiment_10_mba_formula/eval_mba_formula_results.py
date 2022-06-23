#!/usr/bin/env python3
"""
Evaluate MBA formula experiment results
"""

import json
from argparse import ArgumentParser
from pathlib import Path
from typing import Any, Dict, List, Tuple

TOOLS = ["sspam", "mba_blast", "neureduce", "lokiattack"]
OPS = ["add", "sub", "and", "or", "xor"]
DEPTHS = list(range(1, 30+1))
NUM_TESTCASES = 10

def parse_data(path: Path) -> Dict[str, Dict[str, List[Tuple[int, int]]]]:
    data: Dict[str, Dict[str, List[Tuple[int, int]]]] = {}
    for tool in Path("./deobfuscation_tools/").resolve().glob("*"):
        # ignore unknown directories
        if tool.name not in TOOLS:
            continue
        # check if we already have results
        stats_file = list(path.glob(f"{tool.name}_stats.json"))
        if not stats_file:
            print(f"Warning: No stats_file found for {tool.name} - skipping..")
            continue
        # parse results
        data[tool.name] = {}
        assert len(stats_file) == 1, "Found multiple stats_*.json " \
            "files:" + "\n".join(map(lambda p: p.as_posix(), stats_file))
        with open(stats_file[0], "r", encoding="utf-8") as f:
            stats_data = json.load(f)
        for (k, v) in stats_data["data"].items():
            op, depth = k.rstrip(".txt").split("_depth", 1)
            depth = int(depth)
            assert op in OPS, f"op='{op}' unknown"
            assert depth in DEPTHS, f"depth='{depth}' unknown"
            success = int(v["success"])
            if data[tool.name].get(op, None) is None:
                data[tool.name][op] = []
            data[tool.name][op].append((depth, success))
    return data


def avg(l: List[int]) -> float:
    return sum(l) / len(l)


def avg_over_ops(data: Dict[str, Dict[str, List[Tuple[int, int]]]]) -> Dict[str, Dict[str, List[Tuple[int, float]]]]:
    new_data: Dict[str, Dict[str, List[Tuple[int, float]]]] = {}
    for tool in data.keys():
        new_data[tool] = {}
        for op in data[tool].keys():
            length = len(data[tool][op])
            new_data[tool]["avg"] = new_data[tool].get("avg", list(zip(range(1, length + 1), [0.]*length)))
            # print(f"data[{tool}][{op}]={data[tool][op]}")
            # print(f"data[{tool}][avg]={new_data[tool]["avg"]}")
            for depth, num_exprs_simplified in sorted(data[tool][op]):
                for (i, (cur_depth, cur_num)) in enumerate(new_data[tool]["avg"]):
                    if cur_depth == depth:
                        assert depth == cur_depth, f"Expected depth={depth} -- found {cur_depth}"
                        new_data[tool]["avg"][i] = (depth, cur_num + num_exprs_simplified)
        for (i, (depth, sum_exprs)) in enumerate(new_data[tool]["avg"]):
            new_data[tool]["avg"][i] = (depth, sum_exprs / len(data[tool].keys()))
        # print(f"avg[{tool}]={new_data[tool]}")
    return new_data


def main(path: Path) -> None:
    data = parse_data(path)
    avg_data: Dict[str, Dict[str, List[Tuple[int, float]]]] = avg_over_ops(data)

    print("Printing table of simplified MBAs (averaged over all operations per depth):\n")
    table_str = "Depths      "
    for depth in DEPTHS:
        table_str += f"  {depth:>5}"
    table_str += "\n"
    for tool_name, tool_data in avg_data.items():
        table_str += f"{tool_name:<12}"
        for data in tool_data.values(): # type: ignore
            for e in data:
                avg_simplified = e[1]
                if avg_simplified == 0:  # type: ignore
                    table_str += f"  {int(avg_simplified):>4}%"
                else:
                    percentage = round(100 * avg_simplified / NUM_TESTCASES, 1)  # type: ignore
                    table_str += f"  {percentage:>4}%"
        table_str += "\n"
    print(table_str)



if __name__ == "__main__":
    parser = ArgumentParser(description="Plot results")
    parser.add_argument("path", type=Path, help="Path to $TOOL_stats.json files directory")
    args = parser.parse_args()

    main(args.path)

