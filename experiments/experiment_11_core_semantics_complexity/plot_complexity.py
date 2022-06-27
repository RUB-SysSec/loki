#!/usr/bin/env python3

"""
Plot core semantics complexity (depth with and without superoperators)

Python dependencies:
python3 -m pip install matplotlib

Dependencies (if using Latex):
sudo apt install texlive texlive-latex-extra texlive-fonts-recommended dvipng
"""

import json
import matplotlib.pyplot as plt
from argparse import ArgumentParser, Namespace
from matplotlib.patches import Patch
from pathlib import Path
from typing import List, Dict, Iterator, Union, Tuple


# Use LaTeX for titles etc. - default = no to avoid dependencies
USE_LATEX = False
FILE_TYPE = "png"


def parse_data(complexity_data: Path) -> Dict[str, List[Dict[str, int]]]:
    with open(complexity_data, "r", encoding="utf-8") as f:
        data: Dict[str, List[Dict[str, int]]] = json.load(f)
    return data


def get_avg_val_cnts(data: Union[List[Dict[str, int]], List[Dict[int, float]]]) -> Dict[int, float]:
    """
    Given a list of dicts (individual instances listing depth: #handlers_on_this_depth)
    1. Get absolute cnt per depth
    2. Avg cnt over #instances
    3. Convert depth from str to int
    """
    if not data:
        return {}
    # sum all values
    depth_to_sum_cnt: Dict[Union[str, int], Union[int, float]] = {}
    for entry in data:
        for (k, v) in entry.items():
            depth_to_sum_cnt[k] = depth_to_sum_cnt.get(k, 0) + v
    # average over len(data)
    depth_to_avg_sum_cnt: Dict[int, float] = {}
    for k, val in depth_to_sum_cnt.items():
        depth_to_avg_sum_cnt[int(k)] = val / len(data)
    return depth_to_avg_sum_cnt


def d_to_sorted_tuple(d: Dict[int, float]) -> Iterator[Tuple[int, float]]:
    for k in sorted(d):
        yield (k, d[k])


def avg(l: List[int]) -> float:
    return sum(l) / len(l)


def plot(data: Dict[str, List[Dict[str, int]]]) -> None:
    if USE_LATEX:
        params = {"text.usetex" : True,
                "font.size" : 8,
                "font.family" : "Latin Modern Math",
                }

        plt.rcParams.update(params)

    fig, ax = plt.subplots(1, 1)
    fig.set_size_inches(3.57,2)

    keys = ["aes","des", "md5", "rc4", "sha1"]

    color_with_superop = "tab:red"
    color_no_superop = "tab:blue"

    legend_elements = [
                    Patch(facecolor=color_with_superop, edgecolor=color_with_superop,label="With Superoperators"),
                    Patch(facecolor=color_no_superop, edgecolor="black", hatch="/"*4, label="No Superoperators" ),
                    ]

    # Create the figure
    ax.legend(handles=legend_elements)

    ax.set_title("Complexity of Generated Handlers")

    # With superoperator
    key_avgs = []
    # Get average
    for key in keys:
        key_avgs.append(get_avg_val_cnts(data[key + "_with_superoperator"]))
    # Reuse function to sum values and average over our five targets
    wi_sup_data = list(d_to_sorted_tuple(get_avg_val_cnts(key_avgs)))
    ax.bar(
        [x for (x, _) in wi_sup_data], [y for (_, y) in wi_sup_data],
        color=color_with_superop, align="edge", alpha=0.9, width=0.4
    )

    avg_core_semantics_per_binary = avg(list(map(lambda k: sum(list(k.values())), key_avgs)))
    print(f"Average core semantics per binary (with superoperator): {round(avg_core_semantics_per_binary, 2)}")

    # Without superoperator
    key_avgs = []
    for key in keys:
        key_avgs.append(get_avg_val_cnts(data[key + "_no_superoperator"]))
    # Reuse function to sum values and average over our five targets
    no_sup_data = list(d_to_sorted_tuple(get_avg_val_cnts(key_avgs)))
    ax.bar(
        [x for (x, _) in no_sup_data], [y for (_, y) in no_sup_data],
        color=color_no_superop, align="edge", alpha=0.9, width=-0.4, hatch="/"*3
    )

    avg_core_semantics_per_binary = avg(list(map(lambda k: sum(list(k.values())), key_avgs)))
    print(f"Average core semantics per binary (no superoperator): {round(avg_core_semantics_per_binary, 2)}")


    ax.set_xticks([t for t in range(0,24) if t%2==0])
    ax.set_xlabel("Semantic Depth")
    ax.set_ylabel("Average Number of Semantics")

    plot_file_name = F"core_semantics_complexity.{FILE_TYPE}"
    plt.savefig( plot_file_name, dpi=1000, bbox_inches="tight", )

    # plt.show()


def main(args: Namespace) -> None:
    data = parse_data(args.complexity_data_path)
    plot(data)


if __name__ == "__main__":
    parser = ArgumentParser(description="Plot complexity of core semantics")
    parser.add_argument("complexity_data_path", type=Path,
                        help="Path to complexity_data.txt created by eval_complexity.py")
    main(parser.parse_args())
