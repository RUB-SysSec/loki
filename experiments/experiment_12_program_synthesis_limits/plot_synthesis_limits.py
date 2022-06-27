#!/usr/bin/env python3

"""
Plot synthesis limits results
"""

import json
import matplotlib.pyplot as plt
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import List, Tuple
from scipy.stats import beta


PLOT_FILE_TYPE = "png"


def plot(levels: List[Tuple[int, int]], num_expressions: int) -> None:
    ## avoid Latex dependency
    # params = {"text.usetex" : True,
    #         "font.size" : 8,
    #         "font.family" : "Latin Modern Math",
    #         }
    # plt.rcParams.update(params)

    fig, ax = plt.subplots(1, 1)
    fig.set_size_inches(3.57,2)

    x = [x for (x,_) in levels]
    y = [y / num_expressions for (_,y) in levels]
    errs = [ (y / num_expressions, beta.interval(0.999, y, num_expressions - y)) for (_,y) in levels]
    errs[0]=(1.0, (1.0,1.0))
    errs[1]=(1.0, (1.0,1.0))
    errmin = [y-m for (y,(m,_)) in errs]
    errmax = [m-y for (y,(_,m)) in errs]

    print(repr(x))
    print(errmin)

    ax.set_title("Probability of Synthesizing Formulas of Depth $N$")
    ax.plot(x,y, marker="o", color="black", lw=0, markersize=0.7)
    ax.errorbar(
        x, y, yerr=[errmin,errmax], color="black", fmt="none",  marker="o", capsize=1, lw=0.5, markeredgewidth=0.5
    )
    ax.set_xticks([0] + [t for t in x if t%2==0])
    ax.set_yticks([i/100 for i in range(0, 120, 20)])
    ax.set_xlabel("Semantic Depth")
    ax.set_ylabel("Probablity (99.9 \% confidence interval)")

    plot_file_name = f"synthesis_limits.{PLOT_FILE_TYPE}"
    print(f"Saving to '{plot_file_name}'")

    plt.savefig(
        plot_file_name,
        #This is a simple recomendation for publication plots
        dpi=1000,
        # Plot will be occupy a maximum of available space
        bbox_inches="tight",
    )

    #plt.show()


def parse_data(path: Path) -> List[Tuple[int, int]]:
    data: List[Tuple[int, int]] = []
    for file_ in path.glob("*.json"):
        with open(file_, "r", encoding="utf-8") as f:
            content = json.load(f)
        results = content["results"]
        assert results["success"] + results["non_success"] == results["number_of_tasks"]
        # paper has 10_000 expressions per layer, proposed reproduction 100
        if results["number_of_tasks"] not in (100, 10_000):
            print(f"[!] Number of tasks: {results['number_of_tasks']}")
        data.append((content["expression_depth"], results["success"]))
    data = sorted(data, key=lambda t: t[0])
    return data


def main(args: Namespace) -> None:
    data = parse_data(args.path)
    plot(data, args.num_expressions)


if __name__ == "__main__":
    parser = ArgumentParser(description="Plot synthesis limits")
    parser.add_argument("path", type=Path, help="Path to directory containing synthesis limits files")
    parser.add_argument("num_expressions", type=int, help="Number of expressions used for each synthesis depth")
    main(parser.parse_args())
