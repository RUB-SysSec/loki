#!/usr/bin/env python3
"""Plot MBA formula result data"""

import json
import matplotlib.pyplot as plt
import numpy as np
from argparse import ArgumentParser
from matplotlib.patches import Patch
from matplotlib.ticker import FormatStrFormatter
from pathlib import Path
from scipy.ndimage.filters import gaussian_filter1d
from typing import Any, Dict, List, Tuple



TOOLS = ["sspam", "mba_blast", "neureduce", "lokiattack"]
OPS = ["add", "sub", "and", "or", "xor"]
DEPTHS = list(range(1, 30+1))
NUM_TESTCASES = 10

FILE_TYPE = "png" # pdf

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

def plot_plot(ax: Any, color: str, data: List[Tuple[int, int]], **kwargs: Dict[str, Any]) -> None:
    # Plot
    x = np.array([x for (x, _) in data])
    y = np.array([y for (_, y) in data])
    y_smooth = gaussian_filter1d(y, sigma=2.5)
    ax.plot(x, y_smooth, color=color, alpha=0.9, markersize=4, **kwargs)


def plot_tool(*args: List[Any], **kwargs: Dict[str, Any]) -> None:
    plot_plot(*args, **kwargs) # type: ignore


def plot(data: Dict[str, Dict[str, List[Tuple[int, int]]]], op: str) -> None:
    print(f"Plotting {op}..")

    # this would require Latex
    # params = {"text.usetex" : True,
    #           "font.size" : 8,
    #           "mathtext.fontset" : "stix",
    #           "font.family" : "STIXGeneral",
    #           }

    # plt.rcParams.update(params)

    # https://www.color-hex.com/color-palette/114926
    toolcolor: Dict[str, str] = {
        "lokiattack"     : "#466da5",
        "mba_blast"      : "#4e6d4a",
        "sspam"          : "#b4343f",
        "neureduce"      : "#e0c02b",
    }

    fig, ax = plt.subplots(figsize=(4.5,3))
    ax.set_ylim(-2, NUM_TESTCASES)
    ax.set_xlim(1, 30)
    # Logscale
    # ax.set_yscale("log")
    ax.yaxis.set_major_formatter(FormatStrFormatter("%d"))
    ax.set_xlabel("Recursive Expression Rewriting Bound")
    ax.set_ylabel("#Simplified")

    ax.set_title(f"Deobfuscation of {NUM_TESTCASES} MBA formulas")

    # mark Loki's standard recursive rewriting bound area
    ax.axvspan(xmin=20, xmax=30, ymin=0, ymax=NUM_TESTCASES, facecolor="black", alpha=0.1)
    ax.grid(alpha=0.2)

    if data.get("lokiattack", ""):
        print("LokiAttack..")
        plot_tool(
            ax, toolcolor["lokiattack"], data["lokiattack"][op], marker="o",  # type: ignore
            markevery=(0,5), linestyle="dashed", label="LokiAttack"  # type: ignore
        )
    if data.get("mba_blast", ""):
        print("MBA Blast bar..")
        plot_tool(
            ax, toolcolor["mba_blast"], data["mba_blast"][op], marker="x",  # type: ignore
            markevery=(1,4), linestyle="solid", label="MBA Blast" # type: ignore
        )
    if data.get("sspam", ""):
        print("SSPAM bar..")
        plot_tool(
            ax, toolcolor["sspam"], data["sspam"][op], marker="v",  # type: ignore
            markevery=(2,4), linestyle="dashed", label="SSPAM"  # type: ignore
        )
    if data.get("neureduce", ""):
        print("Neureduce bar..")
        plot_tool(
            ax, toolcolor["neureduce"], data["neureduce"][op], marker="^",  # type: ignore
            markevery=(3,4), linestyle="solid", label="NeuReduce"  # type: ignore
        )

    # Create the figure
    ax.legend(loc="upper right")

    fig.tight_layout()
    plt.savefig(f"./plot_{op}.{FILE_TYPE}")
    plt.close()


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
        print(f"avg[{tool}]={new_data[tool]}")
    return new_data



def main(ty: str, data: Dict[str, Dict[str, List[Tuple[int, int]]]]) -> None:
    if ty in OPS:
        plot(data, ty)
    elif ty == "avg":
        new_data = avg_over_ops(data)
        plot(new_data, "avg") # type: ignore
    elif ty == "all":
        for op in OPS:
            plot(data, op)
        new_data = avg_over_ops(data)
        plot(new_data, "avg") # type: ignore




if __name__ == "__main__":
    parser = ArgumentParser(description="Plot results")
    parser.add_argument("path", type=Path, help="Path to $TOOL_stats.json files directory")
    parser.add_argument("type", type=str, default="all", help="Path to data")
    args = parser.parse_args()

    main(args.type, parse_data(args.path))
